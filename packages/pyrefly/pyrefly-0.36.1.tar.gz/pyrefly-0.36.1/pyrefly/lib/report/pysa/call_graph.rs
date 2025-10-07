/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use std::collections::HashMap;
use std::hash::Hash;

use pyrefly_python::ast::Ast;
use pyrefly_python::module_name::ModuleName;
use pyrefly_types::types::Type;
use ruff_python_ast::Expr;
use ruff_python_ast::ExprAttribute;
use ruff_python_ast::ExprName;
use ruff_python_ast::ModModule;
use ruff_python_ast::Stmt;
use ruff_python_ast::StmtClassDef;
use ruff_python_ast::StmtFunctionDef;
use ruff_text_size::Ranged;
use ruff_text_size::TextRange;
use serde::Serialize;

use crate::report::pysa::ast_visitor::AstScopedVisitor;
use crate::report::pysa::ast_visitor::Scopes;
use crate::report::pysa::ast_visitor::visit_module_ast;
use crate::report::pysa::class::ClassRef;
use crate::report::pysa::context::ModuleContext;
use crate::report::pysa::function::FunctionBaseDefinition;
use crate::report::pysa::function::FunctionRef;
use crate::report::pysa::function::WholeProgramFunctionDefinitions;
use crate::report::pysa::location::PysaLocation;
use crate::report::pysa::module::ModuleId;
use crate::state::lsp::FindPreference;

#[derive(Debug, PartialEq, Eq, Clone, Serialize)]
pub enum ImplicitReceiver {
    TrueWithClassReceiver,
    TrueWithObjectReceiver,
    False,
}

pub trait TargetTrait: std::fmt::Debug + PartialEq + Eq + Clone + Hash + Serialize {}

impl TargetTrait for FunctionRef {}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct CallTarget<Target: TargetTrait> {
    pub(crate) target: Target,
    pub(crate) implicit_receiver: ImplicitReceiver,
    pub(crate) receiver_class: Option<ClassRef>,
}

impl<Target: TargetTrait> CallTarget<Target> {
    #[cfg(test)]
    fn map_target<OutputTarget: TargetTrait, MapTarget>(
        self,
        map: MapTarget,
    ) -> CallTarget<OutputTarget>
    where
        MapTarget: Fn(Target) -> OutputTarget,
    {
        CallTarget {
            target: map(self.target),
            implicit_receiver: self.implicit_receiver,
            receiver_class: self.receiver_class,
        }
    }

    #[cfg(test)]
    pub fn with_implicit_receiver(mut self, implicit_receiver: ImplicitReceiver) -> Self {
        self.implicit_receiver = implicit_receiver;
        self
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct CallCallees<Target: TargetTrait> {
    pub(crate) call_targets: Vec<CallTarget<Target>>,
}

impl<Target: TargetTrait> CallCallees<Target> {
    #[cfg(test)]
    fn map_target<OutputTarget: TargetTrait, MapTarget>(
        self,
        map: MapTarget,
    ) -> CallCallees<OutputTarget>
    where
        MapTarget: Fn(Target) -> OutputTarget,
    {
        CallCallees {
            call_targets: self
                .call_targets
                .into_iter()
                .map(|call_target| CallTarget::map_target(call_target, &map))
                .collect(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct AttributeAccessCallees<Target: TargetTrait> {
    pub(crate) callable_targets: Vec<CallTarget<Target>>,
}

impl<Target: TargetTrait> AttributeAccessCallees<Target> {
    #[cfg(test)]
    fn map_target<OutputTarget: TargetTrait, MapTarget>(
        self,
        map: MapTarget,
    ) -> AttributeAccessCallees<OutputTarget>
    where
        MapTarget: Fn(Target) -> OutputTarget,
    {
        AttributeAccessCallees {
            callable_targets: self
                .callable_targets
                .into_iter()
                .map(|call_target| CallTarget::map_target(call_target, &map))
                .collect(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct IdentifierCallees<Target: TargetTrait> {
    pub(crate) callable_targets: Vec<CallTarget<Target>>,
}

impl<Target: TargetTrait> IdentifierCallees<Target> {
    #[cfg(test)]
    fn map_target<OutputTarget: TargetTrait, MapTarget>(
        self,
        map: MapTarget,
    ) -> IdentifierCallees<OutputTarget>
    where
        MapTarget: Fn(Target) -> OutputTarget,
    {
        IdentifierCallees {
            callable_targets: self
                .callable_targets
                .into_iter()
                .map(|call_target| CallTarget::map_target(call_target, &map))
                .collect(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub enum ExpressionCallees<Target: TargetTrait> {
    Call(CallCallees<Target>),
    Identifier(IdentifierCallees<Target>),
    AttributeAccess(AttributeAccessCallees<Target>),
}

impl<Target: TargetTrait> ExpressionCallees<Target> {
    #[cfg(test)]
    pub fn map_target<OutputTarget: TargetTrait, MapTarget>(
        self,
        map: MapTarget,
    ) -> ExpressionCallees<OutputTarget>
    where
        MapTarget: Fn(Target) -> OutputTarget,
    {
        match self {
            ExpressionCallees::Call(call_callees) => {
                ExpressionCallees::Call(call_callees.map_target(map))
            }
            ExpressionCallees::Identifier(identifier_callees) => {
                ExpressionCallees::Identifier(identifier_callees.map_target(map))
            }
            ExpressionCallees::AttributeAccess(attribute_access_callees) => {
                ExpressionCallees::AttributeAccess(attribute_access_callees.map_target(map))
            }
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct CallGraph<Target: TargetTrait>(HashMap<PysaLocation, ExpressionCallees<Target>>);

impl<Target: TargetTrait> CallGraph<Target> {
    #[cfg(test)]
    pub fn from_map(map: HashMap<PysaLocation, ExpressionCallees<Target>>) -> Self {
        Self(map)
    }

    #[cfg(test)]
    pub fn into_iter(self) -> impl Iterator<Item = (PysaLocation, ExpressionCallees<Target>)> {
        self.0.into_iter()
    }

    #[cfg(test)]
    pub fn iter(&self) -> impl Iterator<Item = (&PysaLocation, &ExpressionCallees<Target>)> {
        self.0.iter()
    }
}

impl<Target: TargetTrait> Default for CallGraph<Target> {
    fn default() -> Self {
        Self(HashMap::new())
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CallGraphs<Target: TargetTrait>(HashMap<Target, CallGraph<Target>>);

impl<Target: TargetTrait> CallGraphs<Target> {
    pub fn new() -> Self {
        Self(HashMap::new())
    }

    #[cfg(test)]
    pub fn from_map(map: HashMap<Target, CallGraph<Target>>) -> Self {
        Self(map)
    }

    pub fn into_iter(self) -> impl Iterator<Item = (Target, CallGraph<Target>)> {
        self.0.into_iter()
    }

    #[cfg(test)]
    pub fn iter(&self) -> impl Iterator<Item = (&Target, &CallGraph<Target>)> {
        self.0.iter()
    }

    #[cfg(test)]
    pub fn intersect(&mut self, other: &Self) {
        self.0.retain(|target, _| other.0.contains_key(target));
    }
}

macro_rules! debug_println {
    ($debug:expr, $($arg:tt)*) => {
        if $debug {
            tracing::info!($($arg)*);
        }
    };
}

fn has_toplevel_call(body: &[Stmt], callee_name: &'static str) -> bool {
    body.iter().any(|stmt| match stmt {
        Stmt::Expr(stmt_expr) => match &*stmt_expr.value {
            Expr::Call(call) => match &*call.func {
                Expr::Name(name) => name.id == callee_name,
                _ => false,
            },
            _ => false,
        },
        _ => false,
    })
}

// This also strips `Optional[T]` since that is represented by `Union`
fn strip_none_from_union(type_: &Type) -> Type {
    match type_ {
        Type::Union(types) => {
            if let Ok(none_index) = types.binary_search(&Type::None) {
                let mut new_types = types.clone();
                new_types.remove(none_index);
                match new_types.len() {
                    0 => panic!("Unexpected union type `{:#?}`", type_),
                    1 => new_types.into_iter().next().unwrap(),
                    _ => Type::Union(new_types),
                }
            } else {
                type_.clone()
            }
        }
        _ => type_.clone(),
    }
}

struct MethodMetadata {
    is_staticmethod: bool,
    is_classmethod: bool,
    is_method: bool,
}

fn has_implicit_receiver(
    method_metadata: &MethodMetadata,
    is_receiver_class_def: bool,
) -> ImplicitReceiver {
    if method_metadata.is_staticmethod {
        ImplicitReceiver::False
    } else if method_metadata.is_classmethod {
        if is_receiver_class_def {
            // C.f() where f is a class method
            ImplicitReceiver::TrueWithClassReceiver
        } else {
            // c.f() where f is a class method
            ImplicitReceiver::TrueWithObjectReceiver
        }
    } else if method_metadata.is_method {
        if is_receiver_class_def {
            // C.g(c) where g is a method
            ImplicitReceiver::False
        } else {
            // c.g() where g is a method
            ImplicitReceiver::TrueWithObjectReceiver
        }
    } else {
        ImplicitReceiver::False
    }
}

struct CallGraphVisitor<'a> {
    call_graphs: &'a mut CallGraphs<FunctionRef>,
    module_context: &'a ModuleContext<'a>,
    module_id: ModuleId,
    module_name: ModuleName,
    function_base_definitions: &'a WholeProgramFunctionDefinitions<FunctionBaseDefinition>,
    current_function: Option<FunctionRef>, // The current function, if it is exported.
    debug: bool,                           // Enable logging for the current function or class body.
    debug_scopes: Vec<bool>,               // The value of the debug flag for each scope.
}

impl<'a> CallGraphVisitor<'a> {
    fn add_callees(&mut self, location: TextRange, callees: ExpressionCallees<FunctionRef>) {
        assert!(
            self.call_graphs
                .0
                .entry(self.current_function.clone().unwrap())
                .or_default()
                .0
                .insert(
                    PysaLocation::new(self.module_context.module_info.display_range(location)),
                    callees,
                )
                .is_none(),
            "Adding callees to the same location"
        );
    }

    fn receiver_class_from_type(
        &self,
        receiver_type: &Type,
        is_class_method: bool,
    ) -> (Option<ClassRef>, bool) {
        let receiver_type = strip_none_from_union(receiver_type);
        match receiver_type {
            Type::ClassType(class_type) => (
                Some(ClassRef::from_class(
                    class_type.class_object(),
                    self.module_context.module_ids,
                )),
                false, // Whether the receiver is `type(SomeClass)`
            ),
            Type::ClassDef(class_def) => {
                // The receiver is the class itself. Technically, the receiver class type should be `type(SomeClass)`.
                // However, we strip away the `type` part since it is implied by the `is_class_method` flag.
                (
                    if is_class_method {
                        Some(ClassRef::from_class(
                            &class_def,
                            self.module_context.module_ids,
                        ))
                    } else {
                        None
                    },
                    true,
                )
            }
            _ => (None, false),
        }
    }

    fn get_method_metadata(&self, function_ref: &FunctionRef) -> MethodMetadata {
        self.function_base_definitions
            .get(self.module_id, &function_ref.function_id)
            .map_or(
                MethodMetadata {
                    is_staticmethod: false,
                    is_classmethod: false,
                    is_method: false,
                },
                |function_definition| MethodMetadata {
                    is_staticmethod: function_definition.is_staticmethod,
                    is_classmethod: function_definition.is_classmethod,
                    is_method: FunctionBaseDefinition::is_method(function_definition),
                },
            )
    }

    fn resolve_name(&self, name: &ExprName) -> Vec<CallTarget<FunctionRef>> {
        let identifier = Ast::expr_name_identifier(name.clone());
        self.module_context
            .transaction
            .find_definition_for_name_use(
                self.module_context.handle,
                &identifier,
                &FindPreference::default(),
            )
            .map_or(vec![], |d| vec![d])
            .iter()
            .filter_map(|definition| {
                FunctionRef::from_find_definition_item_with_docstring(
                    definition,
                    self.function_base_definitions,
                    self.module_context,
                )
                .map(|function_ref| {
                    let method_metadata = self.get_method_metadata(&function_ref);
                    let implicit_receiver = has_implicit_receiver(
                        &method_metadata,
                        false, // We don't know receiver type
                    );
                    CallTarget {
                        target: function_ref,
                        implicit_receiver,
                        receiver_class: None,
                    }
                })
            })
            .collect::<Vec<_>>()
    }

    fn resolve_attribute_access(&self, attribute: &ExprAttribute) -> Vec<CallTarget<FunctionRef>> {
        self.module_context
            .transaction
            .find_definition_for_attribute(
                self.module_context.handle,
                attribute.value.range(),
                &attribute.attr,
                &FindPreference::default(),
            )
            .iter()
            .filter_map(|definition| {
                FunctionRef::from_find_definition_item_with_docstring(
                    definition,
                    self.function_base_definitions,
                    self.module_context,
                )
                .map(|function_ref| {
                    let method_metadata = self.get_method_metadata(&function_ref);
                    let (receiver_class, is_receiver_class_def) = self
                        .module_context
                        .answers
                        .get_type_trace(attribute.value.range())
                        .map_or((None, false), |receiver_type| {
                            self.receiver_class_from_type(
                                &receiver_type,
                                method_metadata.is_classmethod,
                            )
                        });
                    let implicit_receiver =
                        has_implicit_receiver(&method_metadata, is_receiver_class_def);
                    CallTarget {
                        target: function_ref,
                        implicit_receiver,
                        receiver_class,
                    }
                })
            })
            .collect::<Vec<_>>()
    }

    // Enable debug logs by adding `pysa_dump()` to the top level statements of the definition of interest
    const DEBUG_FUNCTION_NAME: &'static str = "pysa_dump";

    fn enter_debug_scope(&mut self, body: &[Stmt]) {
        self.debug = has_toplevel_call(body, Self::DEBUG_FUNCTION_NAME);
        self.debug_scopes.push(self.debug);
    }

    fn exit_debug_scope(&mut self) {
        self.debug_scopes.pop();
        self.debug = self.debug_scopes.last().copied().unwrap();
    }
}

impl<'a> AstScopedVisitor for CallGraphVisitor<'a> {
    fn on_scope_update(&mut self, scopes: &Scopes) {
        self.current_function = scopes.current_exported_function(
            self.module_id,
            self.module_name,
            /* include_top_level */ true,
            /* include_class_top_level */ true,
            /* include_decorators_in_decorated_definition */ true,
        );
    }

    fn enter_function_scope(&mut self, function_def: &StmtFunctionDef, _: &Scopes) {
        self.enter_debug_scope(&function_def.body);
    }

    fn enter_class_scope(&mut self, class_def: &StmtClassDef, _: &Scopes) {
        self.enter_debug_scope(&class_def.body);
    }

    fn exit_function_scope(&mut self, _function_def: &StmtFunctionDef, _: &Scopes) {
        self.exit_debug_scope();
    }

    fn exit_class_scope(&mut self, _function_def: &StmtClassDef, _: &Scopes) {
        self.exit_debug_scope();
    }

    fn enter_toplevel_scope(&mut self, ast: &ModModule, _: &Scopes) {
        self.enter_debug_scope(&ast.body);
    }

    fn visit_expression(&mut self, expr: &Expr, _: &Scopes) {
        if self.current_function.is_none() {
            return;
        }

        match expr {
            Expr::Call(call) => {
                debug_println!(self.debug, "Visiting call: {:#?}", call);

                let call_targets = match &*call.func {
                    Expr::Name(name) => self.resolve_name(name),
                    Expr::Attribute(attribute) => self.resolve_attribute_access(attribute),
                    _ => Vec::new(),
                };
                if !call_targets.is_empty() {
                    self.add_callees(
                        expr.range(),
                        ExpressionCallees::Call(CallCallees { call_targets }),
                    );
                }
            }
            Expr::Name(name) => {
                // TODO: Avoid visiting when the parent expression is a `Call`
                let callable_targets = self.resolve_name(name);
                if !callable_targets.is_empty() {
                    self.add_callees(
                        expr.range(),
                        ExpressionCallees::Identifier(IdentifierCallees { callable_targets }),
                    );
                }
            }
            Expr::Attribute(attribute) => {
                // TODO: Avoid visiting when the parent expression is a `Call`
                let callable_targets = self.resolve_attribute_access(attribute);
                if !callable_targets.is_empty() {
                    self.add_callees(
                        expr.range(),
                        ExpressionCallees::AttributeAccess(AttributeAccessCallees {
                            callable_targets,
                        }),
                    );
                }
            }
            _ => (),
        };
    }
}

pub fn export_call_graphs(
    context: &ModuleContext,
    function_base_definitions: &WholeProgramFunctionDefinitions<FunctionBaseDefinition>,
) -> CallGraphs<FunctionRef> {
    let mut call_graphs = CallGraphs::new();

    let mut visitor = CallGraphVisitor {
        call_graphs: &mut call_graphs,
        module_context: context,
        module_id: context.module_id,
        module_name: context.module_info.name(),
        function_base_definitions,
        current_function: None,
        debug: false,
        debug_scopes: Vec::new(),
    };

    visit_module_ast(&mut visitor, context);
    call_graphs
}

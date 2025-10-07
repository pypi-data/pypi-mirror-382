/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use pyrefly_derive::TypeEq;
use pyrefly_derive::VisitMut;

use crate::binding::pydantic::PydanticValidationFlags;

/// Configuration for a Pydantic model.
#[derive(Clone, Debug, TypeEq, PartialEq, Eq, VisitMut, Default)]
pub struct PydanticConfig {
    pub frozen: bool,
    pub validation_flags: PydanticValidationFlags,
    pub extra: bool,
    pub strict: bool,
    pub pydantic_model_kind: PydanticModelKind,
}

#[derive(Clone, Debug, TypeEq, PartialEq, Eq, VisitMut, Default)]

pub enum PydanticModelKind {
    #[default]
    BaseModel,
    RootModel,
}

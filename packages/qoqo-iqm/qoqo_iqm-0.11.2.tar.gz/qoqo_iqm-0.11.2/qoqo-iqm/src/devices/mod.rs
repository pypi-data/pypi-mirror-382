// Copyright © 2020-2023 HQS Quantum Simulations GmbH. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
// in compliance with the License. You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software distributed under the
// License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
// express or implied. See the License for the specific language governing permissions and
// limitations under the License.

//! qoqo-iqm devices
//!

mod deneb_device;
pub use deneb_device::*;

mod resonator_free_device;
pub use resonator_free_device::*;

mod garnet_device;
pub use garnet_device::*;

use pyo3::prelude::*;

/// IQM Devices
#[pymodule]
pub fn iqm_devices(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<DenebDeviceWrapper>()?;
    m.add_class::<ResonatorFreeDeviceWrapper>()?;
    m.add_class::<GarnetDeviceWrapper>()?;
    Ok(())
}

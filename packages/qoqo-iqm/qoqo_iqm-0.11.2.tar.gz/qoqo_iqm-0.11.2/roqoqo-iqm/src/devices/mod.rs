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

//! IQM Devices
//!
//! Provides the devices that are used to execute quantum programs with the IQM backend.

use ndarray::Array2;
use roqoqo::devices::{Device, GenericDevice};

mod deneb_device;
pub use deneb_device::DenebDevice;

mod resonator_free_device;
pub use resonator_free_device::ResonatorFreeDevice;

mod garnet_device;
pub use garnet_device::GarnetDevice;

/// Collection of IQM quantum devices
#[derive(Debug, PartialEq, Eq, Clone, serde::Serialize, serde::Deserialize)]
pub enum IqmDevice {
    /// IQM Deneb device
    DenebDevice(DenebDevice),
    /// Device like Deneb but without the central resonator
    ResonatorFreeDevice(ResonatorFreeDevice),
    /// IQM Garnet device
    GarnetDevice(GarnetDevice),
}

impl IqmDevice {
    /// Returns the remote_host url endpoint of the device
    pub fn remote_host(&self) -> String {
        match self {
            IqmDevice::DenebDevice(x) => x.remote_host(),
            IqmDevice::ResonatorFreeDevice(_) => "".to_string(),
            IqmDevice::GarnetDevice(x) => x.remote_host(),
        }
    }

    /// Returns the name of the device.
    pub fn name(&self) -> String {
        match self {
            IqmDevice::DenebDevice(x) => x.name(),
            IqmDevice::ResonatorFreeDevice(_) => "".to_string(),
            IqmDevice::GarnetDevice(x) => x.name(),
        }
    }
}

impl From<&DenebDevice> for IqmDevice {
    fn from(input: &DenebDevice) -> Self {
        Self::DenebDevice(input.clone())
    }
}
impl From<DenebDevice> for IqmDevice {
    fn from(input: DenebDevice) -> Self {
        Self::DenebDevice(input)
    }
}

impl From<&GarnetDevice> for IqmDevice {
    fn from(input: &GarnetDevice) -> Self {
        Self::GarnetDevice(input.clone())
    }
}
impl From<GarnetDevice> for IqmDevice {
    fn from(input: GarnetDevice) -> Self {
        Self::GarnetDevice(input)
    }
}

impl From<&ResonatorFreeDevice> for IqmDevice {
    fn from(input: &ResonatorFreeDevice) -> Self {
        Self::ResonatorFreeDevice(input.clone())
    }
}
impl From<ResonatorFreeDevice> for IqmDevice {
    fn from(input: ResonatorFreeDevice) -> Self {
        Self::ResonatorFreeDevice(input)
    }
}

/// Implements the Device trait for IqmDevice.
///
/// Defines standard functions available for roqoqo-iqm devices.
impl Device for IqmDevice {
    /// Returns the gate time of a single qubit operation if the single qubit operation is available on device.
    ///
    /// # Arguments
    ///
    /// * `hqslang` - The hqslang name of a single qubit gate.
    /// * `qubit` - The qubit the gate acts on
    ///
    /// # Returns
    ///
    /// * `Some<f64>` - The gate time.
    /// * `None` - The gate is not available on the device.
    fn single_qubit_gate_time(&self, hqslang: &str, qubit: &usize) -> Option<f64> {
        match self {
            IqmDevice::DenebDevice(x) => x.single_qubit_gate_time(hqslang, qubit),
            IqmDevice::ResonatorFreeDevice(x) => x.single_qubit_gate_time(hqslang, qubit),
            IqmDevice::GarnetDevice(x) => x.single_qubit_gate_time(hqslang, qubit),
        }
    }

    /// Returns the gate time of a two qubit operation if the two qubit operation is available on device.
    ///
    /// # Arguments
    ///
    /// * `hqslang` - The hqslang name of a two qubit gate.
    /// * `control` - The control qubit the gate acts on
    /// * `target` - The target qubit the gate acts on
    ///
    /// # Returns
    ///
    /// * `Some<f64>` - The gate time.
    /// * `None` - The gate is not available on the device.
    fn two_qubit_gate_time(&self, hqslang: &str, control: &usize, target: &usize) -> Option<f64> {
        match self {
            IqmDevice::DenebDevice(x) => x.two_qubit_gate_time(hqslang, control, target),
            IqmDevice::ResonatorFreeDevice(x) => x.two_qubit_gate_time(hqslang, control, target),
            IqmDevice::GarnetDevice(x) => x.two_qubit_gate_time(hqslang, control, target),
        }
    }

    /// Returns the gate time of a three qubit operation if the three qubit operation is available on device.
    ///
    /// # Arguments
    ///
    /// * `hqslang` - The hqslang name of a two qubit gate.
    /// * `control` - The control qubit the gate acts on
    /// * `target` - The target qubit the gate acts on
    ///
    /// # Returns
    ///
    /// * `Some<f64>` - The gate time.
    /// * `None` - The gate is not available on the device.
    fn three_qubit_gate_time(
        &self,
        hqslang: &str,
        control_0: &usize,
        control_1: &usize,
        target: &usize,
    ) -> Option<f64> {
        match self {
            IqmDevice::DenebDevice(x) => {
                x.three_qubit_gate_time(hqslang, control_0, control_1, target)
            }
            IqmDevice::ResonatorFreeDevice(x) => {
                x.three_qubit_gate_time(hqslang, control_0, control_1, target)
            }
            IqmDevice::GarnetDevice(x) => {
                x.three_qubit_gate_time(hqslang, control_0, control_1, target)
            }
        }
    }

    /// Returns the gate time of a multi qubit operation if the multi qubit operation is available on device.
    ///
    /// # Arguments
    ///
    /// * `hqslang` - The hqslang name of a multi qubit gate.
    /// * `qubits` - The qubits the gate acts on
    ///
    /// # Returns
    ///
    /// * `Some<f64>` - The gate time.
    /// * `None` - The gate is not available on the device.
    fn multi_qubit_gate_time(&self, hqslang: &str, qubits: &[usize]) -> Option<f64> {
        match self {
            IqmDevice::DenebDevice(x) => x.multi_qubit_gate_time(hqslang, qubits),
            IqmDevice::ResonatorFreeDevice(x) => x.multi_qubit_gate_time(hqslang, qubits),
            IqmDevice::GarnetDevice(x) => x.multi_qubit_gate_time(hqslang, qubits),
        }
    }

    /// Returns the matrix of the decoherence rates of the Lindblad equation.
    ///
    /// $$
    /// \frac{d}{dt}\rho = \sum_{i,j=0}^{2} M_{i,j} L_{i} \rho L_{j}^{\dagger} - \frac{1}{2} \{ L_{j}^{\dagger} L_i, \rho \} \\\\
    ///     L_0 = \sigma^{+} \\\\
    ///     L_1 = \sigma^{-} \\\\
    ///     L_3 = \sigma^{z}
    /// $$
    ///
    /// # Arguments
    ///
    /// * `qubit` - The qubit for which the rate matrix is returned.
    ///
    /// # Returns
    ///
    /// * `Some<Array2<f64>>` - The decoherence rates.
    /// * `None` - The qubit is not part of the device.
    fn qubit_decoherence_rates(&self, qubit: &usize) -> Option<Array2<f64>> {
        match self {
            IqmDevice::DenebDevice(x) => x.qubit_decoherence_rates(qubit),
            IqmDevice::ResonatorFreeDevice(x) => x.qubit_decoherence_rates(qubit),
            IqmDevice::GarnetDevice(x) => x.qubit_decoherence_rates(qubit),
        }
    }

    /// Returns the number of qubits the device supports.
    ///
    /// # Returns
    ///
    /// * `usize` - The number of qubits in the device.
    fn number_qubits(&self) -> usize {
        match self {
            IqmDevice::DenebDevice(x) => x.number_qubits(),
            IqmDevice::ResonatorFreeDevice(x) => x.number_qubits(),
            IqmDevice::GarnetDevice(x) => x.number_qubits(),
        }
    }

    /// Returns the list of pairs of qubits linked with a native two-qubit-gate in the device.
    ///
    /// A pair of qubits is considered linked by a native two-qubit-gate if the device
    /// can implement a two-qubit-gate between the two qubits without decomposing it
    /// into a sequence of gates that involves a third qubit of the device.
    /// The two-qubit-gate also has to form a universal set together with the available
    /// single qubit gates.
    ///
    /// The returned vectors is a simple, graph-library independent, representation of
    /// the undirected connectivity graph of the device.
    /// It can be used to construct the connectivity graph in a graph library of the users
    /// choice from a list of edges and can be used for applications like routing in quantum algorithms.
    ///
    /// # Returns
    ///
    /// * `Vec<(usize, usize)>` - A list (Vec) of pairs of qubits linked with a native two-qubit-gate in the device.
    fn two_qubit_edges(&self) -> Vec<(usize, usize)> {
        match self {
            IqmDevice::DenebDevice(x) => x.two_qubit_edges(),
            IqmDevice::ResonatorFreeDevice(x) => x.two_qubit_edges(),
            IqmDevice::GarnetDevice(x) => x.two_qubit_edges(),
        }
    }

    /// Turns Device into GenericDevice
    ///
    /// Can be used as a generic interface for devices when a boxed dyn trait object cannot be used
    /// (for example when the interface needs to be serialized)
    ///
    /// # Note
    ///
    /// [crate::devices::GenericDevice] uses nested HashMaps to represent the most general device connectivity.
    /// The memory usage will be inefficient for devices with large qubit numbers.
    ///
    /// # Returns
    ///
    /// * `GenericDevice` - A generic device representation of the device.
    fn to_generic_device(&self) -> GenericDevice {
        match self {
            IqmDevice::DenebDevice(x) => x.to_generic_device(),
            IqmDevice::ResonatorFreeDevice(x) => x.to_generic_device(),
            IqmDevice::GarnetDevice(x) => x.to_generic_device(),
        }
    }
}

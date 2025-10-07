// Copyright © 2020-2023 HQS Quantum Simulations GmbH. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
// in compliance with the License. You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software distributed under the License
// is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
// or implied. See the License for the specific language governing permissions and limitations under
// the License.

use ndarray::Array2;
use roqoqo::devices::{Device, GenericDevice};
use std::cmp::{max, min};

/// IQM Garnet device
///
/// A hardware device with 20 qubits arranged in a square lattice.
#[derive(Debug, PartialEq, Eq, Clone, serde::Serialize, serde::Deserialize)]
pub struct GarnetDevice {
    url: String,
    name: String,
}

impl GarnetDevice {
    /// Create new GarnetDevice with default settings.
    pub fn new() -> Self {
        Self {
            url: "https://cocos.resonance.meetiqm.com/garnet/jobs".to_string(),
            name: "Garnet".to_string(),
        }
    }

    /// Returns API endpoint URL of the device.
    pub fn remote_host(&self) -> String {
        self.url.clone()
    }

    /// Returns the name of the device.
    pub fn name(&self) -> String {
        self.name.clone()
    }

    /// Change API endpoint URL of the device
    ///
    /// # Arguments
    ///
    /// * `new_url` - The new URL to set.
    pub fn set_endpoint_url(&mut self, new_url: String) {
        self.url = new_url
    }
}

/// Implements the Device trait for GarnetDevice.
///
/// Defines standard functions available for roqoqo-iqm devices.
impl Device for GarnetDevice {
    /// Returns the gate time of a one-qubit operation if the operation is available on device.
    ///
    /// # Arguments
    ///
    /// * `hqslang` - The hqslang name of a single-qubit gate.
    /// * `qubit` - The qubit the gate acts on
    ///
    /// # Returns
    ///
    /// * `Some<f64>` - The gate time.
    /// * `None` - The gate is not available on the device.
    fn single_qubit_gate_time(&self, hqslang: &str, qubit: &usize) -> Option<f64> {
        if hqslang == "RotateXY" && qubit < &self.number_qubits() {
            Some(1.0)
        } else {
            None
        }
    }

    /// Returns the gate time of a two-qubit operation if the operation is available on device.
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
        if hqslang == "ControlledPauliZ"
            && self
                .two_qubit_edges()
                .contains(&(min(*control, *target), max(*control, *target)))
        {
            Some(1.0)
        } else {
            None
        }
    }

    /// Returns the gate time of a three-qubit operation if the three-qubit operation is available on device.
    ///
    /// # Arguments
    ///
    /// * `hqslang` - The hqslang name of a three qubit gate.
    /// * `control` - The control qubit the gate acts on
    /// * `target` - The target qubit the gate acts on
    ///
    /// # Returns
    ///
    /// * `Some<f64>` - The gate time.
    /// * `None` - The gate is not available on the device.
    fn three_qubit_gate_time(
        &self,
        _hqslang: &str,
        _control_0: &usize,
        _control_1: &usize,
        _target: &usize,
    ) -> Option<f64> {
        None
    }

    /// Returns the gate time of a multi-qubit operation if the multi-qubit operation is available on device.
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
    fn multi_qubit_gate_time(&self, _hqslang: &str, _qubits: &[usize]) -> Option<f64> {
        None
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
    fn qubit_decoherence_rates(&self, _qubit: &usize) -> Option<Array2<f64>> {
        None
    }

    /// Returns the number of qubits the device supports.
    ///
    /// # Returns
    ///
    /// * `usize`- The number of qubits in the device.
    fn number_qubits(&self) -> usize {
        20
    }

    /// Returns the list of pairs of qubits linked with a native two-qubit-gate in the device.
    ///
    /// A pair of qubits is considered linked by a native two-qubit-gate if the device
    /// can implement a two-qubit-gate between the two qubits without decomposing it
    /// into a sequence of gates that involves a third qubit of the device.
    /// The two-qubit-gate also has to form a universal set together with the available
    /// single-qubit gates.
    ///
    /// The returned vectors is a simple, graph-library independent, representation of the
    /// undirected connectivity graph of the device. It can be used to construct the connectivity
    /// graph in a graph library of the users choice from a list of edges and can be used for
    /// applications like routing in quantum algorithms.
    ///
    /// # Returns
    ///
    /// * `Vec<(usize, usize)>` - A list (Vec) of pairs of qubits linked with a native two-qubit-gate in the device.
    fn two_qubit_edges(&self) -> Vec<(usize, usize)> {
        vec![
            (1, 2),
            (1, 4),
            (2, 5),
            (3, 4),
            (3, 8),
            (4, 5),
            (4, 9),
            (5, 6),
            (5, 10),
            (6, 7),
            (6, 11),
            (7, 12),
            (8, 9),
            (8, 13),
            (9, 10),
            (9, 14),
            (10, 11),
            (10, 15),
            (11, 12),
            (11, 16),
            (12, 17),
            (13, 14),
            (14, 15),
            (14, 18),
            (15, 16),
            (15, 19),
            (16, 17),
            (16, 20),
            (18, 19),
            (19, 20),
        ]
    }

    /// Turns Device into GenericDevice.
    ///
    /// Can be used as a generic interface for devices when a boxed dyn trait object cannot be used
    /// (for example when the interface needs to be serialized)
    ///
    /// # Note
    ///
    /// [crate::devices::GenericDevice] uses nested HashMaps to represent the most general device
    /// connectivity. The memory usage will be inefficient for devices with large qubit numbers.
    ///
    /// # Returns
    ///
    /// * `GenericDevice` - A generic device representation of the device.
    fn to_generic_device(&self) -> GenericDevice {
        let mut generic_device = GenericDevice::new(self.number_qubits());
        for qubit in 0..self.number_qubits() {
            generic_device
                .set_single_qubit_gate_time(
                    "RotateXY",
                    qubit,
                    self.single_qubit_gate_time("RotateXY", &qubit).unwrap(),
                )
                .expect("Unexpectedly failed to add single-qubit gate time to generic device.");
        }
        for (qb1, qb2) in self.two_qubit_edges() {
            generic_device
                .set_two_qubit_gate_time(
                    "ControlledPauliZ",
                    qb1,
                    qb2,
                    self.two_qubit_gate_time("ControlledPauliZ", &qb1, &qb2)
                        .unwrap(),
                )
                .expect("Unexpectedly failed to add two-qubit gate time to generic device.");
            // Exchange control and target
            generic_device
                .set_two_qubit_gate_time(
                    "ControlledPauliZ",
                    qb2,
                    qb1,
                    self.two_qubit_gate_time("ControlledPauliZ", &qb2, &qb1)
                        .unwrap(),
                )
                .expect("Unexpectedly failed to add two-qubit gate time to generic device.");
        }
        generic_device
    }
}

impl Default for GarnetDevice {
    fn default() -> Self {
        Self::new()
    }
}

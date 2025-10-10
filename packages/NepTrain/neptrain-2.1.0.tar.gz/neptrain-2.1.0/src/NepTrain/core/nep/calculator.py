#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/21 14:22
# @Author  : 兵
# @email    : 1747193328@qq.com
import contextlib
import os

import numpy as np
from ase import Atoms

from NepTrain.nep_cpu import CpuNep

class Nep3Calculator:

    def __init__(self, model_file="nep.txt"):
        if not isinstance(model_file, str):
            model_file=str(model_file,encoding="utf-8")
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                self.nep3 = CpuNep(model_file)
        self.element_list=self.nep3.get_element_list()
        self.type_dict = {e: i for i, e in enumerate(self.element_list)}




    def get_descriptors(self,structure):
        symbols = structure.get_chemical_symbols()
        _type = [self.type_dict[k] for k in symbols]
        _box = structure.cell.transpose(1, 0).reshape(-1).tolist()
        _position = structure.get_positions().transpose(1, 0).reshape(-1).tolist()
        descriptor = self.nep3.get_descriptor(_type, _box, _position)
        descriptors_per_atom = np.array(descriptor).reshape(-1, len(structure)).T

        return descriptors_per_atom
    def get_structure_descriptors(self, structure):
        descriptors_per_atom=self.get_descriptors(structure)
        return descriptors_per_atom.mean(axis=0)

    def get_structures_descriptors(self,structures:[Atoms]):
        _types=[]
        _boxs=[]
        _positions=[]

        for structure in structures:
            symbols = structure.get_chemical_symbols()
            _type = [self.type_dict[k] for k in symbols]
            _box = structure.cell.transpose(1, 0).reshape(-1).tolist()
            _position = structure.get_positions().transpose(1, 0).reshape(-1).tolist()
            _types.append(_type)
            _boxs.append(_box)
            _positions.append(_position)

        descriptor = self.nep3.get_descriptors(_types, _boxs, _positions)

        return np.array(descriptor)


    def calculate(self,structures:list[Atoms]):
        group_size=[]
        _types = []
        _boxs = []
        _positions = []
        if isinstance(structures, Atoms):
            structures = [structures]
        for structure in structures:
            symbols = structure.get_chemical_symbols()
            _type = [self.type_dict[k] for k in symbols]
            _box = structure.cell.transpose(1, 0).reshape(-1).tolist()
            _position = structure.get_positions().transpose(1, 0).reshape(-1).tolist()
            _types.append(_type)
            _boxs.append(_box)
            _positions.append(_position)
            group_size.append(len(_type))

        potentials, forces, virials = self.nep3.calculate(_types, _boxs, _positions)


        split_indices = np.cumsum(group_size)[:-1]
        #
        potentials=np.hstack(potentials)
        split_potential_arrays = np.split(potentials, split_indices)
        potentials_array = np.array(list(map(np.sum, split_potential_arrays)))
        # print(potentials_array)

        # 处理每个force数组：reshape (3, -1) 和 transpose(1, 0)
        reshaped_forces = [np.array(force).reshape(3, -1).T for force in forces]

        forces_array = np.vstack(reshaped_forces)
        # print(forces_array)

        reshaped_virials = np.vstack([np.array(virial).reshape(9, -1).mean(axis=1) for virial in virials])

        # virials_array = reshaped_virials[:,[0,4,8,1,5,6]]
        virials_array=reshaped_virials
        return potentials_array,forces_array,virials_array


class DescriptorCalculator:
    def __init__(self, calculator_type="nep",**calculator_kwargs):
        self.calculator_type=calculator_type
        if calculator_type == "nep":
            self.calculator=Nep3Calculator(**calculator_kwargs)
        elif calculator_type == "soap":
            from dscribe.descriptors import SOAP

            self.calculator = SOAP(
                **calculator_kwargs,dtype="float32"
            )
        else:
            raise ValueError("calculator_type must be nep or soap")


    def get_structures_descriptors(self,structures:[Atoms]):

        if len(structures)==0:
            return np.array([])

        if self.calculator_type == "nep":
            return self.calculator.get_structures_descriptors(structures)
        else:

            return  np.array([self.calculator.create_single(structure).mean(0) for structure in structures])


if __name__ == '__main__':
    nep3 = Nep3Calculator(model_file="/mnt/d/Desktop/vispy/KNbO3/nep.txt")
    from ase.io import read
    import time
    structures = read("/mnt/d/Desktop/vispy/KNbO3/train.xyz",index=":")
    start=time.time()

    descriptors = nep3.get_structures_descriptors(structures)
    print(f"计算描述符：{len(structures)}个结构，耗时：{time.time()-start:.3f}s")
    print("descriptors",descriptors.shape)
    start=time.time()

    potentials ,forces ,virials   = nep3.calculate(structures)

    print(f"计算性质：{len(structures)}个结构，耗时：{time.time()-start:.3f}s")
    print("potentials",potentials.shape)
    print("forces",forces.shape)
    print("virials",virials.shape)


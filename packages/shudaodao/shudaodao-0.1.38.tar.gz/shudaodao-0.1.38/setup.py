#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/8/21 下午9:48
# @Desc     ：
import os
from pathlib import Path

from Cython.Build import cythonize
from setuptools import Extension, find_namespace_packages, find_packages
from setuptools import setup


def _get_cython_extensions() -> list[Extension]:
    """自动发现所有 .c 文件并为其创建 Cython 扩展对象"""
    ext_modules = []

    packages = find_packages(where=str(Path("src").resolve()))
    relative_path = Path("src")

    for package in packages:
        package_path = relative_path / package.replace('.', '/')
        for c_file in package_path.rglob("*.c"):
            # 构建模块路径
            rel_path = c_file.relative_to(relative_path)
            module_name = str(rel_path.with_suffix(''))
            if "/" in module_name:
                module_name = module_name.replace('/', '.')
            if "\\" in module_name:
                module_name = module_name.replace('\\', '.')

            compile_args = [] if os.name == 'nt' else ["-Wno-unreachable-code-fallthrough",
                                                       "-Wno-unused-function",
                                                       "-Wno-unreachable-code", ]

            ext_modules.append(
                Extension(
                    name=module_name,
                    sources=[str(c_file)],
                    extra_compile_args=compile_args,
                )
            )
    return ext_modules


setup(
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=False,
    ext_modules=cythonize(
        _get_cython_extensions(),
        compiler_directives={
            'language_level': 3,
            'annotation_typing': True,
        },
        # quiet=True,
        annotate=True,
        nthreads=4,  # 使用多线程编译
    ),
    # script_args=['build_ext'],
    zip_safe=False,
)

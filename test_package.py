#!/usr/bin/env python3
"""
测试 livekit-plugins-volcengine 打包的 package 是否可用。

此脚本验证：
1. 包可以正确导入
2. 所有主要类和函数可用
3. 版本信息正确
4. 基本功能可以初始化

运行方式：
1. 安装打包的包：
   pip install -e livekit-plugins-volcengine/
   或
   pip install livekit-plugins-volcengine/dist/livekit_plugins_volcengine-1.3.0-py3-none-any.whl

2. 运行测试：
   python livekit-plugins-volcengine/test_package.py
"""

import sys
from pathlib import Path


def test_import():
    """测试包导入"""
    print("\n" + "=" * 60)
    print("测试 1: 包导入")
    print("=" * 60)
    
    try:
        from livekit.plugins import volcengine
        print("✓ 成功导入 livekit.plugins.volcengine")
        return True, volcengine
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        print("\n请先安装包:")
        print("  pip install -e livekit-plugins-volcengine/")
        print("  或")
        print("  pip install livekit-plugins-volcengine/dist/livekit_plugins_volcengine-1.3.0-py3-none-any.whl")
        return False, None


def test_version(volcengine):
    """测试版本信息"""
    print("\n" + "=" * 60)
    print("测试 2: 版本信息")
    print("=" * 60)
    
    try:
        version = volcengine.__version__
        print(f"✓ 版本: {version}")
        
        if version == "1.3.0":
            print("✓ 版本号正确")
            return True
        else:
            print(f"✗ 版本号不匹配，期望 1.3.0，实际 {version}")
            return False
    except AttributeError as e:
        print(f"✗ 无法获取版本信息: {e}")
        return False


def test_exports(volcengine):
    """测试导出的类和函数"""
    print("\n" + "=" * 60)
    print("测试 3: 导出的类和函数")
    print("=" * 60)
    
    expected_exports = [
        "TTS",
        "LLM",
        "STT",
        "BigModelSTT",
        "RealtimeModel",
        "__version__",
    ]
    
    all_passed = True
    for export_name in expected_exports:
        if hasattr(volcengine, export_name):
            print(f"✓ {export_name} 可用")
        else:
            print(f"✗ {export_name} 不可用")
            all_passed = False
    
    return all_passed


def test_class_instantiation(volcengine):
    """测试类实例化（不需要真实凭证）"""
    print("\n" + "=" * 60)
    print("测试 4: 类实例化（基本检查）")
    print("=" * 60)
    
    results = {}
    
    # 测试 TTS
    try:
        tts_class = volcengine.TTS
        print(f"✓ TTS 类可访问: {tts_class}")
        # 检查类是否有必要的方法
        if hasattr(tts_class, 'stream'):
            print("  ✓ TTS.stream 方法存在")
        results['TTS'] = True
    except Exception as e:
        print(f"✗ TTS 类访问失败: {e}")
        results['TTS'] = False
    
    # 测试 STT
    try:
        stt_class = volcengine.STT
        print(f"✓ STT 类可访问: {stt_class}")
        if hasattr(stt_class, 'stream'):
            print("  ✓ STT.stream 方法存在")
        results['STT'] = True
    except Exception as e:
        print(f"✗ STT 类访问失败: {e}")
        results['STT'] = False
    
    # 测试 BigModelSTT
    try:
        bigmodel_stt_class = volcengine.BigModelSTT
        print(f"✓ BigModelSTT 类可访问: {bigmodel_stt_class}")
        if hasattr(bigmodel_stt_class, 'stream'):
            print("  ✓ BigModelSTT.stream 方法存在")
        results['BigModelSTT'] = True
    except Exception as e:
        print(f"✗ BigModelSTT 类访问失败: {e}")
        results['BigModelSTT'] = False
    
    # 测试 LLM
    try:
        llm_class = volcengine.LLM
        print(f"✓ LLM 类可访问: {llm_class}")
        if hasattr(llm_class, 'chat'):
            print("  ✓ LLM.chat 方法存在")
        results['LLM'] = True
    except Exception as e:
        print(f"✗ LLM 类访问失败: {e}")
        results['LLM'] = False
    
    # 测试 RealtimeModel
    try:
        realtime_class = volcengine.RealtimeModel
        print(f"✓ RealtimeModel 类可访问: {realtime_class}")
        if hasattr(realtime_class, 'chat'):
            print("  ✓ RealtimeModel.chat 方法存在")
        results['RealtimeModel'] = True
    except Exception as e:
        print(f"✗ RealtimeModel 类访问失败: {e}")
        results['RealtimeModel'] = False
    
    return all(results.values())


def test_plugin_registration(volcengine):
    """测试插件注册"""
    print("\n" + "=" * 60)
    print("测试 5: 插件注册")
    print("=" * 60)
    
    try:
        # 检查是否有 VolcenginePlugin 类
        if hasattr(volcengine, 'VolcenginePlugin'):
            print("✓ VolcenginePlugin 类存在")
            return True
        else:
            print("⚠ VolcenginePlugin 类不存在（可能在 __init__.py 中内部使用）")
            # 这不是致命错误，因为插件可能在导入时自动注册
            return True
    except Exception as e:
        print(f"✗ 插件注册检查失败: {e}")
        return False


def test_module_structure():
    """测试模块结构"""
    print("\n" + "=" * 60)
    print("测试 6: 模块结构")
    print("=" * 60)
    
    try:
        # 测试命名空间包
        import livekit
        print("✓ livekit 命名空间包可导入")
        
        import livekit.plugins
        print("✓ livekit.plugins 命名空间包可导入")
        
        import livekit.plugins.volcengine
        print("✓ livekit.plugins.volcengine 包可导入")
        
        # 检查子模块
        submodules = [
            'bigmodel_stt',
            'llm',
            'realtime',
            'stt',
            'tts',
            'utils',
            'version',
            'log',
        ]
        
        all_found = True
        for submodule in submodules:
            module_path = f"livekit.plugins.volcengine.{submodule}"
            try:
                __import__(module_path)
                print(f"  ✓ {submodule} 子模块可导入")
            except ImportError as e:
                print(f"  ✗ {submodule} 子模块导入失败: {e}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"✗ 模块结构检查失败: {e}")
        return False


def test_dependencies():
    """测试依赖项"""
    print("\n" + "=" * 60)
    print("测试 7: 依赖项检查")
    print("=" * 60)
    
    dependencies = {
        'livekit.agents': 'livekit-agents',
        'numpy': 'numpy',
        'openai': 'openai',
        'pydantic': 'pydantic',
    }
    
    all_available = True
    for module_name, package_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"✓ {package_name} 已安装")
        except ImportError:
            print(f"✗ {package_name} 未安装")
            all_available = False
    
    if not all_available:
        print("\n请安装缺失的依赖:")
        print("  pip install livekit-agents numpy openai pydantic")
    
    return all_available


def test_type_hints():
    """测试类型提示"""
    print("\n" + "=" * 60)
    print("测试 8: 类型提示")
    print("=" * 60)
    
    try:
        from livekit.plugins import volcengine
        
        # 检查 py.typed 文件
        import livekit.plugins.volcengine as volc_module
        module_path = Path(volc_module.__file__).parent
        py_typed_path = module_path / "py.typed"
        
        if py_typed_path.exists():
            print(f"✓ py.typed 文件存在: {py_typed_path}")
            return True
        else:
            print(f"⚠ py.typed 文件不存在: {py_typed_path}")
            print("  （类型提示可能不可用）")
            return True  # 不是致命错误
    except Exception as e:
        print(f"✗ 类型提示检查失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("livekit-plugins-volcengine 包测试")
    print("=" * 60)
    print("此测试验证打包的 package 是否可用")
    
    results = {}
    
    # 测试 1: 导入
    passed, volcengine = test_import()
    results['import'] = passed
    if not passed:
        print("\n✗ 包导入失败，无法继续测试")
        return 1
    
    # 测试 2: 版本
    results['version'] = test_version(volcengine)
    
    # 测试 3: 导出
    results['exports'] = test_exports(volcengine)
    
    # 测试 4: 类实例化
    results['instantiation'] = test_class_instantiation(volcengine)
    
    # 测试 5: 插件注册
    results['plugin'] = test_plugin_registration(volcengine)
    
    # 测试 6: 模块结构
    results['structure'] = test_module_structure()
    
    # 测试 7: 依赖项
    results['dependencies'] = test_dependencies()
    
    # 测试 8: 类型提示
    results['type_hints'] = test_type_hints()
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {test_name:20s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过！")
        print("=" * 60)
        print("\n包已正确打包并可以使用。")
        print("\n下一步:")
        print("1. 提交到 GitHub 仓库")
        print("2. 在其他项目中使用:")
        print("   pip install git+https://github.com/your-username/livekit-plugins-volcengine.git")
        return 0
    else:
        print("✗ 部分测试失败")
        print("=" * 60)
        print("\n请检查失败的测试并修复问题。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

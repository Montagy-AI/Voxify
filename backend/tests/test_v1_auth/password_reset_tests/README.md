# Password Reset Tests

这个文件夹包含了Voxify密码重置功能的所有测试文件。

## 📁 文件结构

```
password_reset_tests/
├── __init__.py                      # Python包初始化文件
├── README.md                        # 本说明文件
├── run_all_tests.py                 # 测试运行器 - 运行所有测试
├── test_password_reset_unit.py      # 单元测试 - 工具函数和邮件服务
└── test_password_reset_simple.py   # 简化集成测试 - 核心工作流
```

## 🧪 测试内容

### 单元测试 (test_password_reset_unit.py)
- ✅ 密码重置令牌生成和验证
- ✅ 令牌过期时间管理
- ✅ 邮件服务配置和发送
- ✅ 邮件模板生成
- ✅ SMTP连接测试

### 简化集成测试 (test_password_reset_simple.py)
- ✅ 完整的密码重置工作流逻辑
- ✅ 邮件模板内容验证
- ✅ 安全验证功能测试
- ✅ 令牌唯一性测试
- ✅ 邮件发送功能测试（使用mock）

## 🚀 运行测试

### 运行所有测试
```bash
cd backend/tests/test_v1_auth/password_reset_tests
python run_all_tests.py
```

### 运行单个测试文件
```bash
# 运行单元测试
python test_password_reset_unit.py

# 运行简化集成测试
python test_password_reset_simple.py
```

## ✅ 测试结果

当前所有测试都通过：
- **总测试数**: 22个
- **成功率**: 100%
- **状态**: ✅ ALL TESTS PASSED!

## 📋 测试覆盖

- **令牌管理**: 生成、验证、过期处理
- **邮件服务**: 配置、模板、发送
- **安全机制**: 输入验证、防护措施
- **工作流程**: 完整的密码重置流程

## 🔧 维护说明

- 所有测试都使用mock来避免实际的邮件发送
- 测试使用内存数据库，不依赖外部数据库配置
- 测试文件包含详细的文档字符串和注释
- 新增功能时应相应添加测试用例 
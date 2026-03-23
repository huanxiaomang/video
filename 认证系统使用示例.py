"""
JWT + Bcrypt 认证系统使用示例
演示如何在实际项目中使用认证功能
"""

import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

# ============================================
# 第一部分：Bcrypt 密码加密示例
# ============================================

print("=" * 60)
print("第一部分：Bcrypt 密码加密演示")
print("=" * 60)

def hash_password(password: str) -> str:
    """加密密码"""
    # 1. 将密码转为字节
    password_bytes = password.encode('utf-8')

    # 2. 生成盐并加密
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # 3. 转为字符串
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


# 示例1：注册用户时加密密码
print("\n【示例1】用户注册 - 加密密码")
print("-" * 60)

original_password = "admin123"
print(f"原始密码: {original_password}")

# 加密密码
hashed_password = hash_password(original_password)
print(f"加密后密码: {hashed_password}")
print(f"密码长度: {len(hashed_password)} 字符")

# 解析密文结构
print("\n密文结构解析:")
parts = hashed_password.split('$')
print(f"  算法版本: ${parts[1]}")
print(f"  成本因子: ${parts[2]} (2^{parts[2]} = {2**int(parts[2])} 次迭代)")
print(f"  盐值+哈希: {parts[3][:10]}... (共{len(parts[3])}字符)")


# 示例2：同一密码多次加密结果不同
print("\n【示例2】同一密码多次加密")
print("-" * 60)

hash1 = hash_password("admin123")
hash2 = hash_password("admin123")
hash3 = hash_password("admin123")

print(f"第1次加密: {hash1[:40]}...")
print(f"第2次加密: {hash2[:40]}...")
print(f"第3次加密: {hash3[:40]}...")
print(f"\n结果相同吗? {hash1 == hash2}")  # False
print("✅ 每次加密结果都不同，防止彩虹表攻击！")


# 示例3：登录时验证密码
print("\n【示例3】用户登录 - 验证密码")
print("-" * 60)

# 模拟数据库中存储的密码哈希
stored_hash = hash_password("admin123")
print(f"数据库中的密码哈希: {stored_hash[:40]}...")

# 用户输入正确密码
print("\n尝试1: 输入正确密码")
user_input_1 = "admin123"
is_valid_1 = verify_password(user_input_1, stored_hash)
print(f"  输入密码: {user_input_1}")
print(f"  验证结果: {is_valid_1} ✅")

# 用户输入错误密码
print("\n尝试2: 输入错误密码")
user_input_2 = "wrong_password"
is_valid_2 = verify_password(user_input_2, stored_hash)
print(f"  输入密码: {user_input_2}")
print(f"  验证结果: {is_valid_2} ❌")


# ============================================
# 第二部分：JWT Token 生成与验证示例
# ============================================

print("\n\n" + "=" * 60)
print("第二部分：JWT Token 生成与验证演示")
print("=" * 60)

# JWT配置
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT Token"""
    # 1. 复制数据
    to_encode = data.copy()

    # 2. 计算过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 3. 添加过期时间
    to_encode.update({"exp": expire})

    # 4. 生成JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码JWT Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        return {"error": str(e)}


# 示例4：生成JWT Token
print("\n【示例4】登录成功 - 生成Token")
print("-" * 60)

# 用户登录成功后生成Token
username = "admin"
token_data = {"sub": username}  # sub = subject（主题）

access_token = create_access_token(data=token_data)
print(f"用户名: {username}")
print(f"生成的Token: {access_token}")
print(f"Token长度: {len(access_token)} 字符")

# 解析Token结构
print("\nToken结构解析:")
parts = access_token.split('.')
print(f"  Header (头部):    {parts[0][:20]}... ({len(parts[0])} 字符)")
print(f"  Payload (载荷):   {parts[1][:20]}... ({len(parts[1])} 字符)")
print(f"  Signature (签名): {parts[2][:20]}... ({len(parts[2])} 字符)")


# 示例5：解码JWT Token
print("\n【示例5】访问资源 - 验证Token")
print("-" * 60)

# 解码Token
payload = decode_token(access_token)
print("解码后的载荷数据:")
print(f"  用户名 (sub): {payload.get('sub')}")
print(f"  过期时间 (exp): {payload.get('exp')}")

# 转换时间戳为可读格式
exp_timestamp = payload.get('exp')
exp_datetime = datetime.fromtimestamp(exp_timestamp)
print(f"  过期时间 (可读): {exp_datetime}")

# 检查是否过期
now = datetime.utcnow()
is_expired = now.timestamp() > exp_timestamp
print(f"  当前时间: {now}")
print(f"  是否过期: {is_expired}")


# 示例6：Token篡改检测
print("\n【示例6】安全性 - Token篡改检测")
print("-" * 60)

# 原始Token
original_token = access_token
print(f"原始Token: {original_token[:50]}...")

# 尝试篡改Token（修改一个字符）
tampered_token = original_token[:-1] + ('X' if original_token[-1] != 'X' else 'Y')
print(f"篡改Token: {tampered_token[:50]}...")

# 验证原始Token
print("\n验证原始Token:")
result1 = decode_token(original_token)
if 'error' not in result1:
    print(f"  ✅ 验证成功: 用户 {result1.get('sub')}")
else:
    print(f"  ❌ 验证失败: {result1.get('error')}")

# 验证篡改Token
print("\n验证篡改Token:")
result2 = decode_token(tampered_token)
if 'error' not in result2:
    print(f"  ✅ 验证成功: 用户 {result2.get('sub')}")
else:
    print(f"  ❌ 验证失败: {result2.get('error')}")


# 示例7：Token过期测试
print("\n【示例7】Token过期测试")
print("-" * 60)

# 创建一个1秒后过期的Token
short_lived_token = create_access_token(
    data={"sub": "test_user"},
    expires_delta=timedelta(seconds=1)
)
print("创建了一个1秒后过期的Token")

# 立即验证
print("\n立即验证:")
result = decode_token(short_lived_token)
if 'error' not in result:
    print(f"  ✅ Token有效: 用户 {result.get('sub')}")
else:
    print(f"  ❌ Token无效: {result.get('error')}")

# 等待2秒后验证
print("\n等待2秒后验证...")
import time
time.sleep(2)

result = decode_token(short_lived_token)
if 'error' not in result:
    print(f"  ✅ Token有效: 用户 {result.get('sub')}")
else:
    print(f"  ❌ Token已过期: {result.get('error')}")


# ============================================
# 第三部分：完整认证流程模拟
# ============================================

print("\n\n" + "=" * 60)
print("第三部分：完整认证流程模拟")
print("=" * 60)

# 模拟数据库
class MockDatabase:
    def __init__(self):
        self.users = {}

    def create_user(self, username: str, password: str, role: str = "viewer"):
        """创建用户"""
        user_id = f"user_{len(self.users) + 1}"
        self.users[username] = {
            "user_id": user_id,
            "username": username,
            "password_hash": hash_password(password),
            "role": role,
            "created_at": datetime.utcnow()
        }
        return user_id

    def get_user(self, username: str):
        """获取用户"""
        return self.users.get(username)


# 模拟认证服务
class AuthService:
    def __init__(self, db: MockDatabase):
        self.db = db

    def register(self, username: str, password: str, role: str = "viewer"):
        """注册用户"""
        if self.db.get_user(username):
            return {"success": False, "message": "用户已存在"}

        user_id = self.db.create_user(username, password, role)
        return {"success": True, "user_id": user_id, "message": "注册成功"}

    def login(self, username: str, password: str):
        """登录"""
        user = self.db.get_user(username)

        if not user:
            return {"success": False, "message": "用户不存在"}

        if not verify_password(password, user["password_hash"]):
            return {"success": False, "message": "密码错误"}

        # 生成Token
        access_token = create_access_token(data={"sub": username})

        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user["user_id"],
                "username": user["username"],
                "role": user["role"]
            }
        }

    def verify_token(self, token: str):
        """验证Token"""
        payload = decode_token(token)

        if 'error' in payload:
            return {"success": False, "message": payload['error']}

        username = payload.get('sub')
        user = self.db.get_user(username)

        if not user:
            return {"success": False, "message": "用户不存在"}

        return {
            "success": True,
            "user": {
                "user_id": user["user_id"],
                "username": user["username"],
                "role": user["role"]
            }
        }


# 示例8：完整流程演示
print("\n【示例8】完整认证流程")
print("-" * 60)

# 初始化
db = MockDatabase()
auth = AuthService(db)

# 1. 注册用户
print("\n步骤1: 注册用户")
result = auth.register("admin", "admin123", "admin")
print(f"  注册结果: {result}")

# 2. 登录（正确密码）
print("\n步骤2: 登录（正确密码）")
result = auth.login("admin", "admin123")
if result["success"]:
    print(f"  ✅ 登录成功")
    print(f"  用户信息: {result['user']}")
    print(f"  Token: {result['access_token'][:50]}...")

    # 保存Token
    current_token = result['access_token']
else:
    print(f"  ❌ 登录失败: {result['message']}")

# 3. 登录（错误密码）
print("\n步骤3: 登录（错误密码）")
result = auth.login("admin", "wrong_password")
if result["success"]:
    print(f"  ✅ 登录成功")
else:
    print(f"  ❌ 登录失败: {result['message']}")

# 4. 访问受保护资源
print("\n步骤4: 访问受保护资源")
result = auth.verify_token(current_token)
if result["success"]:
    print(f"  ✅ Token验证成功")
    print(f"  当前用户: {result['user']['username']}")
    print(f"  用户角色: {result['user']['role']}")
else:
    print(f"  ❌ Token验证失败: {result['message']}")


# ============================================
# 第四部分：安全性测试
# ============================================

print("\n\n" + "=" * 60)
print("第四部分：安全性测试")
print("=" * 60)

# 示例9：暴力破解难度计算
print("\n【示例9】暴力破解难度分析")
print("-" * 60)

import string

# 计算密码空间
password_length = 8
charset_size = len(string.ascii_letters + string.digits)  # 62个字符
total_combinations = charset_size ** password_length

print(f"密码长度: {password_length} 位")
print(f"字符集大小: {charset_size} (a-z, A-Z, 0-9)")
print(f"可能组合数: {total_combinations:,}")

# Bcrypt计算时间（假设）
bcrypt_time_per_hash = 0.1  # 秒
total_time_seconds = total_combinations * bcrypt_time_per_hash
total_time_years = total_time_seconds / (365.25 * 24 * 3600)

print(f"\nBcrypt计算时间: {bcrypt_time_per_hash} 秒/次")
print(f"暴力破解总时间: {total_time_years:,.0f} 年")
print("✅ 实际上几乎不可能暴力破解！")


# 示例10：常见攻击防护
print("\n【示例10】常见攻击防护演示")
print("-" * 60)

print("\n1. 彩虹表攻击防护:")
print("   - 相同密码，不同盐值 → 不同哈希")
hash_a = hash_password("123456")
hash_b = hash_password("123456")
print(f"   密码1哈希: {hash_a[:30]}...")
print(f"   密码2哈希: {hash_b[:30]}...")
print(f"   是否相同: {hash_a == hash_b} ✅")

print("\n2. Token篡改防护:")
print("   - 修改Token任何部分 → 签名验证失败")
print("   - 已在示例6中演示 ✅")

print("\n3. Token过期防护:")
print("   - 超过有效期 → 自动失效")
print("   - 已在示例7中演示 ✅")

print("\n4. 密码明文泄露防护:")
print("   - 数据库只存哈希 → 无法还原原密码")
print("   - Bcrypt单向加密 ✅")


print("\n\n" + "=" * 60)
print("演示完成！")
print("=" * 60)
print("\n📚 关键要点总结:")
print("  1. Bcrypt: 单向加密 + 自动加盐 + 慢速计算")
print("  2. JWT: 无状态 + 签名验证 + 自动过期")
print("  3. 安全性: 防暴力破解 + 防篡改 + 防泄露")
print("\n💡 建议:")
print("  - 生产环境使用强密钥（SECRET_KEY）")
print("  - 使用HTTPS加密传输")
print("  - 设置合理的Token过期时间")
print("  - 添加登录日志和异常检测")



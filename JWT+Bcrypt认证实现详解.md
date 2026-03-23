# 电厂巡检视频系统 - JWT + Bcrypt 认证实现详解

> 本文档详细讲解项目中如何实现用户认证，包括密码加密存储（Bcrypt）和身份令牌验证（JWT Token）

---

## 📋 目录

1. [认证架构概览](#认证架构概览)
2. [Bcrypt 密码加密实现](#bcrypt-密码加密实现)
3. [JWT Token 认证实现](#jwt-token-认证实现)
4. [完整认证流程](#完整认证流程)
5. [代码实现详解](#代码实现详解)
6. [实际应用示例](#实际应用示例)
7. [安全性分析](#安全性分析)

---

## 🏗️ 认证架构概览

### 系统组成

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  前端客户端  │ ◄─────► │  后端服务器  │ ◄─────► │   数据库    │
│  (Vue3)     │  HTTP   │  (FastAPI)  │  SQL   │  (SQLite)   │
└─────────────┘         └─────────────┘         └─────────────┘
      │                        │                        │
      │                        │                        │
   存储Token              验证Token              存储密码哈希
  localStorage           JWT解码验证            Bcrypt加密
```

### 认证流程图

```
用户操作                前端处理                后端处理                数据库
   │                      │                      │                      │
   ├─ 1.输入账号密码 ──►  │                      │                      │
   │                      ├─ 2.发送登录请求 ──►  │                      │
   │                      │                      ├─ 3.查询用户 ──────►  │
   │                      │                      │ ◄─ 4.返回用户信息 ─  │
   │                      │                      ├─ 5.Bcrypt验证密码    │
   │                      │                      ├─ 6.生成JWT Token     │
   │                      │ ◄─ 7.返回Token ─────  │                      │
   │                      ├─ 8.存储Token         │                      │
   │                      │   (localStorage)     │                      │
   ├─ 9.访问视频页面 ──►  │                      │                      │
   │                      ├─ 10.携带Token请求 ─► │                      │
   │                      │                      ├─ 11.验证Token        │
   │                      │                      ├─ 12.解码用户信息     │
   │                      │ ◄─ 13.返回视频流 ───  │                      │
   │ ◄─ 14.播放视频 ─────  │                      │                      │
```

---

## 🔐 Bcrypt 密码加密实现

### 1. 什么是 Bcrypt？

Bcrypt 是一种**单向加密算法**，专门用于密码存储：
- ✅ **不可逆**：无法从密文还原出原始密码
- ✅ **加盐（Salt）**：每次加密结果都不同，防止彩虹表攻击
- ✅ **慢速计算**：故意设计得很慢，防止暴力破解

### 2. 代码实现位置

**文件：`server/models.py`**

```python
import bcrypt

def hash_password(password: str) -> str:
    """哈希密码"""
    # 1. 将密码转为字节
    password_bytes = password.encode('utf-8')

    # 2. 生成盐（salt）并加密
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # 3. 转为字符串存储
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    # 1. 将输入密码和存储的哈希转为字节
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    # 2. Bcrypt自动提取盐并验证
    return bcrypt.checkpw(plain_bytes, hashed_bytes)
```

### 3. 实际加密过程

#### 注册时加密密码

```python
# 用户注册时（在 models.py 的 init_db 函数中）
admin = User(
    username="admin",
    password_hash=hash_password("admin123"),  # ← 加密密码
    role="admin"
)
```

**加密过程：**
```
原始密码: "admin123"
         ↓
    encode('utf-8')
         ↓
    字节串: b'admin123'
         ↓
    bcrypt.gensalt() → 生成随机盐
         ↓
    bcrypt.hashpw(密码, 盐)
         ↓
存储密文: "$2b$12$KIXxJ3V8h9Zq7X.../abc123xyz..."
```

**密文结构解析：**
```
$2b$12$KIXxJ3V8h9Zq7X.../abc123xyz...
 │  │  │                │
 │  │  │                └─ 实际哈希值（22字符）
 │  │  └─ 盐值（22字符）
 │  └─ 成本因子（2^12 = 4096次迭代）
 └─ 算法版本（2b = Bcrypt）
```

#### 登录时验证密码

```python
# 用户登录时（在 api_auth.py 的 login 函数中）
user = await db.query(User).filter(User.username == "admin").first()

# 验证密码
if verify_password("admin123", user.password_hash):
    print("密码正确！")
else:
    print("密码错误！")
```

**验证过程：**
```
用户输入: "admin123"
         ↓
    encode('utf-8')
         ↓
    字节串: b'admin123'
         ↓
从数据库取出密文: "$2b$12$KIXxJ3V8h9Zq7X.../abc123xyz..."
         ↓
    bcrypt.checkpw(输入密码, 存储密文)
         ↓
    Bcrypt自动：
    1. 从密文中提取盐值
    2. 用相同的盐加密输入密码
    3. 比较两个哈希值
         ↓
    返回 True/False
```

### 4. 为什么安全？

| 攻击方式 | Bcrypt 防护 |
|---------|------------|
| **明文泄露** | 数据库只存密文，看不到原密码 |
| **彩虹表攻击** | 每个密码的盐不同，无法预计算 |
| **暴力破解** | 计算慢（4096次迭代），破解耗时长 |
| **相同密码识别** | 即使密码相同，密文也不同 |

**示例：**
```python
# 两次加密同一个密码
hash1 = hash_password("admin123")
hash2 = hash_password("admin123")

print(hash1)  # $2b$12$abc...
print(hash2)  # $2b$12$xyz...  ← 完全不同！
```

---

## 🎫 JWT Token 认证实现

### 1. 什么是 JWT？

JWT（JSON Web Token）是一种**无状态的身份令牌**：
- ✅ **自包含**：Token 本身包含用户信息，无需查数据库
- ✅ **防篡改**：通过签名验证，任何修改都会被发现
- ✅ **有效期**：可设置过期时间，自动失效

### 2. JWT 结构

JWT 由三部分组成，用 `.` 分隔：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
│                                      │                                      │
└─────────── Header ──────────────────┴─────────── Payload ─────────────────┴─────────── Signature ──────────
```

#### 第一部分：Header（头部）

```json
{
  "alg": "HS256",    // 签名算法
  "typ": "JWT"       // 令牌类型
}
```
Base64编码后 → `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9`

#### 第二部分：Payload（载荷）

```json
{
  "sub": "admin",              // 用户名
  "exp": 1735689600            // 过期时间（Unix时间戳）
}
```
Base64编码后 → `eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIn0`

#### 第三部分：Signature（签名）

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY  // 密钥："your-secret-key-change-this-in-production"
)
```
签名后 → `SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

### 3. 代码实现位置

**文件：`server/config.py`**

```python
class Settings(BaseSettings):
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"  # 签名密钥
    ALGORITHM: str = "HS256"                                       # 签名算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440                        # 24小时过期
```

**文件：`server/api_auth.py`**

```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    # 1. 复制要编码的数据
    to_encode = data.copy()

    # 2. 计算过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=1440)  # 默认24小时

    # 3. 添加过期时间到载荷
    to_encode.update({"exp": expire})

    # 4. 生成JWT
    encoded_jwt = jwt.encode(
        to_encode,                    # 载荷数据
        settings.SECRET_KEY,          # 密钥
        algorithm=settings.ALGORITHM  # 算法
    )

    return encoded_jwt
```

### 4. Token 生成过程

```python
# 登录成功后生成Token
access_token = create_access_token(
    data={"sub": "admin"},  # sub = subject（主题），存储用户名
    expires_delta=timedelta(minutes=1440)
)
```

**生成步骤：**
```
输入数据: {"sub": "admin"}
         ↓
添加过期时间: {"sub": "admin", "exp": 1735689600}
         ↓
创建Header: {"alg": "HS256", "typ": "JWT"}
         ↓
Base64编码Header和Payload
         ↓
用SECRET_KEY签名
         ↓
拼接三部分: Header.Payload.Signature
         ↓
返回完整Token
```

### 5. Token 验证过程

```python
async def get_current_user(token: str, db: AsyncSession):
    """获取当前用户"""
    try:
        # 1. 解码JWT
        payload = jwt.decode(
            token,                        # Token字符串
            settings.SECRET_KEY,          # 密钥（必须和生成时一致）
            algorithms=[settings.ALGORITHM]  # 算法
        )

        # 2. 提取用户名
        username: str = payload.get("sub")

        # 3. 从数据库查询用户
        user = await db.query(User).filter(User.username == username).first()

        return user

    except JWTError:
        # Token无效、过期或被篡改
        raise HTTPException(status_code=401, detail="无法验证凭据")
```

**验证步骤：**
```
接收Token: "eyJhbGci..."
         ↓
分割三部分: Header, Payload, Signature
         ↓
用SECRET_KEY重新计算签名
         ↓
比较签名是否一致
         ↓
检查是否过期（exp字段）
         ↓
解码Payload获取用户信息
         ↓
返回用户数据
```

---

## 🔄 完整认证流程

### 场景 1：用户登录

#### 前端代码（`web-client/src/stores/user.ts`）

```typescript
async function login(username: string, password: string) {
  // 1. 调用登录API
  const response = await loginApi(username, password)

  // 2. 保存Token到localStorage
  localStorage.setItem('access_token', response.access_token)

  // 3. 获取用户信息
  await fetchUserInfo()

  return true
}
```

#### 后端代码（`server/api_auth.py`）

```python
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    # 1. 查询用户
    user = await db.query(User).filter(User.username == form_data.username).first()

    # 2. 验证密码（Bcrypt）
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 3. 生成JWT Token
    access_token = create_access_token(data={"sub": user.username})

    # 4. 返回Token
    return {"access_token": access_token, "token_type": "bearer"}
```

#### 完整流程图

```
┌─────────┐                    ┌─────────┐                    ┌─────────┐
│  浏览器  │                    │  服务器  │                    │  数据库  │
└────┬────┘                    └────┬────┘                    └────┬────┘
     │                              │                              │
     │ 1. POST /api/auth/login      │                              │
     │    username: "admin"         │                              │
     │    password: "admin123"      │                              │
     ├─────────────────────────────►│                              │
     │                              │                              │
     │                              │ 2. SELECT * FROM users       │
     │                              │    WHERE username='admin'    │
     │                              ├─────────────────────────────►│
     │                              │                              │
     │                              │ 3. 返回用户数据               │
     │                              │    password_hash: "$2b$12..."│
     │                              │◄─────────────────────────────┤
     │                              │                              │
     │                              │ 4. Bcrypt验证密码             │
     │                              │    verify_password(          │
     │                              │      "admin123",             │
     │                              │      "$2b$12..."             │
     │                              │    ) → True ✓                │
     │                              │                              │
     │                              │ 5. 生成JWT Token              │
     │                              │    create_access_token(      │
     │                              │      {"sub": "admin"}        │
     │                              │    )                         │
     │                              │                              │
     │ 6. 返回Token                  │                              │
     │    {                         │                              │
     │      "access_token": "eyJ...",                              │
     │      "token_type": "bearer"  │                              │
     │    }                         │                              │
     │◄─────────────────────────────┤                              │
     │                              │                              │
     │ 7. 存储Token                  │                              │
     │    localStorage.setItem(     │                              │
     │      'access_token',         │                              │
     │      'eyJ...'                │                              │
     │    )                         │                              │
     │                              │                              │
```

---

### 场景 2：访问受保护的资源

#### 前端代码（`web-client/src/api/request.ts`）

```typescript
// 请求拦截器：自动添加Token
service.interceptors.request.use((config) => {
  // 从localStorage读取Token
  const token = localStorage.getItem('access_token')

  if (token) {
    // 添加到请求头
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})
```

#### 后端代码（`server/api_devices.py`）

```python
from api_auth import get_current_user

@router.get("/devices")
async def get_devices(
    current_user: User = Depends(get_current_user),  # ← 依赖注入，自动验证Token
    db: AsyncSession = Depends(get_db)
):
    """获取设备列表（需要登录）"""
    # 如果Token无效，get_current_user会抛出401异常
    # 如果Token有效，current_user就是当前登录的用户对象

    devices = await db.query(Device).all()
    return devices
```

#### 完整流程图

```
┌─────────┐                    ┌─────────┐                    ┌─────────┐
│  浏览器  │                    │  服务器  │                    │  数据库  │
└────┬────┘                    └────┬────┘                    └────┬────┘
     │                              │                              │
     │ 1. GET /api/devices          │                              │
     │    Authorization:            │                              │
     │    Bearer eyJhbGci...        │                              │
     ├─────────────────────────────►│                              │
     │                              │                              │
     │                              │ 2. 提取Token                  │
     │                              │    token = "eyJhbGci..."     │
     │                              │                              │
     │                              │ 3. 验证Token签名              │
     │                              │    jwt.decode(               │
     │                              │      token,                  │
     │                              │      SECRET_KEY              │
     │                              │    )                         │
     │                              │                              │
     │                              │ 4. 检查是否过期               │
     │                              │    if exp > now: ✓           │
     │                              │                              │
     │                              │ 5. 提取用户名                 │
     │                              │    username = "admin"        │
     │                              │                              │
     │                              │ 6. 查询用户                   │
     │                              ├─────────────────────────────►│
     │                              │◄─────────────────────────────┤
     │                              │                              │
     │                              │ 7. 查询设备列表               │
     │                              ├─────────────────────────────►│
     │                              │◄─────────────────────────────┤
     │                              │                              │
     │ 8. 返回设备数据               │                              │
     │◄─────────────────────────────┤                              │
     │                              │                              │
```

---

### 场景 3：Token 过期处理

#### 前端代码（`web-client/src/api/request.ts`）

```typescript
// 响应拦截器：处理401错误
service.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效
      ElMessage.error('未授权，请重新登录')

      // 清除Token
      localStorage.removeItem('access_token')

      // 跳转到登录页
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)
```

#### 流程图

```
Token过期时间：2025-01-01 00:00:00
当前时间：    2025-01-01 12:00:00  ← 已过期

┌─────────┐                    ┌─────────┐
│  浏览器  │                    │  服务器  │
└────┬────┘                    └────┬────┘
     │                              │
     │ 1. GET /api/devices          │
     │    Authorization:            │
     │    Bearer eyJhbGci...        │
     ├─────────────────────────────►│
     │                              │
     │                              │ 2. 解码Token
     │                              │    exp = 1735689600
     │                              │    now = 1735732800
     │                              │    exp < now ✗ 已过期！
     │                              │
     │ 3. 返回401错误                │
     │    {                         │
     │      "detail": "无法验证凭据" │
     │    }                         │
     │◄─────────────────────────────┤
     │                              │
     │ 4. 清除Token                  │
     │    localStorage.removeItem() │
     │                              │
     │ 5. 跳转登录页                 │
     │    window.location = '/login'│
     │                              │
```

---

## 💻 代码实现详解

### 1. 数据库模型（`server/models.py`）

```python
class User(Base):
    """用户模型"""
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # ← 存储Bcrypt密文
    role = Column(String(20), default="viewer")          # 用户角色
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**数据库表结构：**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| user_id | String(36) | 用户ID（UUID） | "a1b2c3d4-..." |
| username | String(50) | 用户名（唯一） | "admin" |
| password_hash | String(255) | 密码哈希 | "$2b$12$..." |
| role | String(20) | 角色 | "admin" |
| created_at | DateTime | 创建时间 | 2025-01-01 00:00:00 |

### 2. 认证API（`server/api_auth.py`）

#### 登录接口

```python
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录接口

    请求格式：
        POST /api/auth/login
        Content-Type: multipart/form-data

        username=admin&password=admin123

    返回格式：
        {
          "access_token": "eyJhbGci...",
          "token_type": "bearer"
        }
    """
    try:
        # 1. 查询用户
        result = await db.execute(
            select(User).where(User.username == form_data.username)
        )
        user = result.scalar_one_or_none()

        # 2. 验证用户和密码
        if user is None or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )

        logger.info(f"用户登录成功: {user.username}")

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 获取当前用户接口

```python
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息

    请求格式：
        GET /api/auth/me
        Authorization: Bearer eyJhbGci...

    返回格式：
        {
          "user_id": "a1b2c3d4-...",
          "username": "admin",
          "role": "admin",
          "created_at": "2025-01-01T00:00:00"
        }
    """
    return current_user
```

#### 登出接口

```python
@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    用户登出

    注意：JWT是无状态的，服务器不存储Token
    登出只是前端删除Token，服务器只记录日志
    """
    logger.info(f"用户登出: {current_user.username}")
    return {"message": "登出成功"}
```

### 3. 前端认证（`web-client/src/stores/user.ts`）

```typescript
export const useUserStore = defineStore('user', () => {
  const userInfo = ref<User | null>(null)
  const token = ref<string>('')
  const isLoggedIn = ref<boolean>(false)

  /**
   * 登录
   */
  async function login(username: string, password: string) {
    try {
      // 1. 调用登录API
      const response = await loginApi(username, password)

      // 2. 保存Token
      token.value = response.access_token
      localStorage.setItem('access_token', response.access_token)

      // 3. 获取用户信息
      await fetchUserInfo()

      // 4. 更新登录状态
      isLoggedIn.value = true
      ElMessage.success('登录成功')

      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  /**
   * 登出
   */
  async function logout() {
    try {
      await logoutApi()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      // 清除状态
      userInfo.value = null
      token.value = ''
      isLoggedIn.value = false
      localStorage.removeItem('access_token')
      ElMessage.success('已登出')
    }
  }

  /**
   * 初始化（从localStorage恢复登录状态）
   */
  async function init() {
    const savedToken = localStorage.getItem('access_token')
    if (savedToken) {
      token.value = savedToken
      await fetchUserInfo()
      if (userInfo.value) {
        isLoggedIn.value = true
      }
    }
  }

  return {
    userInfo,
    token,
    isLoggedIn,
    login,
    logout,
    init,
  }
})
```

---

## 🎯 实际应用示例

### 示例 1：创建管理员账户

```python
# 在 server/models.py 的 init_db() 函数中
async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 检查是否已存在管理员
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()

        if not admin:
            # 创建管理员账户
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),  # ← Bcrypt加密
                role="admin"
            )
            session.add(admin)
            await session.commit()
            print("✅ 默认管理员账户已创建: admin / admin123")
```

**数据库中的实际数据：**

```sql
SELECT * FROM users WHERE username = 'admin';

-- 结果：
user_id     | a1b2c3d4-e5f6-7890-abcd-ef1234567890
username    | admin
password_hash | $2b$12$KIXxJ3V8h9Zq7X4Y2Z1A.eB3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q8R
role        | admin
created_at  | 2025-01-01 00:00:00
```

### 示例 2：用户登录流程

**步骤 1：用户在登录页输入账号密码**

```
用户名: admin
密码:   admin123
```

**步骤 2：前端发送登录请求**

```http
POST http://localhost:8000/api/auth/login
Content-Type: multipart/form-data

username=admin&password=admin123
```

**步骤 3：后端验证密码**

```python
# 1. 从数据库查询用户
user = User(
    username="admin",
    password_hash="$2b$12$KIXxJ3V8h9Zq7X4Y2Z1A.eB3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q8R"
)

# 2. Bcrypt验证
verify_password("admin123", user.password_hash)
# → True ✓
```

**步骤 4：生成JWT Token**

```python
access_token = create_access_token(data={"sub": "admin"})
# → "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczNTY4OTYwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
```

**步骤 5：返回Token给前端**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczNTY4OTYwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "token_type": "bearer"
}
```

**步骤 6：前端存储Token**

```typescript
localStorage.setItem('access_token', response.access_token)
```

### 示例 3：访问受保护的API

**步骤 1：前端发送请求（自动添加Token）**

```http
GET http://localhost:8000/api/devices
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczNTY4OTYwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**步骤 2：后端验证Token**

```python
# 1. 提取Token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 2. 解码验证
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
# → {"sub": "admin", "exp": 1735689600}

# 3. 检查过期
if payload["exp"] > time.time():
    # Token有效
    username = payload["sub"]  # "admin"
```

**步骤 3：返回数据**

```json
[
  {
    "device_id": "device-001",
    "device_name": "1号机器人",
    "status": "online"
  }
]
```

---

## 🔒 安全性分析

### 1. Bcrypt 安全性

| 安全特性 | 说明 | 防护效果 |
|---------|------|---------|
| **盐值随机** | 每次加密使用不同的盐 | 防止彩虹表攻击 |
| **慢速哈希** | 4096次迭代计算 | 防止暴力破解 |
| **单向加密** | 无法从密文还原密码 | 数据库泄露也安全 |
| **自适应成本** | 可调整迭代次数 | 随硬件升级保持安全 |

**破解难度计算：**

```
假设密码：8位数字+字母（62^8 = 218万亿种组合）
Bcrypt计算时间：0.1秒/次
暴力破解时间：218万亿 × 0.1秒 = 6900万年
```

### 2. JWT 安全性

| 安全特性 | 说明 | 防护效果 |
|---------|------|---------|
| **签名验证** | HMAC-SHA256签名 | 防止Token篡改 |
| **过期时间** | 24小时自动失效 | 限制Token有效期 |
| **密钥保护** | SECRET_KEY只在服务器 | 无法伪造Token |
| **无状态** | 不存储在数据库 | 减少数据库压力 |

**Token篡改检测：**

```python
# 原始Token
token = "eyJhbGci...正确的签名"

# 黑客尝试修改Payload
tampered_token = "eyJhbGci...修改后的数据.错误的签名"

# 服务器验证
jwt.decode(tampered_token, SECRET_KEY)
# → 抛出异常：Signature verification failed
```

### 3. 潜在风险与防护

| 风险 | 描述 | 本项目的防护措施 |
|------|------|----------------|
| **Token泄露** | Token被窃取 | ✅ 设置24小时过期时间 |
| **XSS攻击** | 脚本窃取Token | ⚠️ 建议：使用HttpOnly Cookie |
| **CSRF攻击** | 跨站请求伪造 | ✅ Token在Header中，不自动发送 |
| **中间人攻击** | 网络监听 | ⚠️ 建议：使用HTTPS加密传输 |
| **密码弱** | 用户设置简单密码 | ⚠️ 建议：添加密码强度验证 |

### 4. 生产环境建议

```python
# ❌ 开发环境配置（不安全）
SECRET_KEY = "your-secret-key-change-this-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

# ✅ 生产环境配置（推荐）
SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # 从环境变量读取
ACCESS_TOKEN_EXPIRE_MINUTES = 60          # 1小时
REFRESH_TOKEN_EXPIRE_DAYS = 7             # 添加刷新Token机制

# ✅ 使用HTTPS
# ✅ 添加速率限制（防止暴力破解）
# ✅ 记录登录日志
# ✅ 实现Token黑名单（登出后立即失效）
```

---

## 📊 总结对比

### Bcrypt vs 其他加密方式

| 加密方式 | 可逆性 | 加盐 | 速度 | 安全性 | 适用场景 |
|---------|-------|------|------|-------|---------|
| **Bcrypt** | ❌ 不可逆 | ✅ 自动 | 🐢 慢 | ⭐⭐⭐⭐⭐ | 密码存储 |
| MD5 | ❌ 不可逆 | ❌ 需手动 | 🚀 快 | ⭐ | 已淘汰 |
| SHA256 | ❌ 不可逆 | ❌ 需手动 | 🚀 快 | ⭐⭐ | 文件校验 |
| AES | ✅ 可逆 | - | 🚀 快 | ⭐⭐⭐⭐ | 数据加密 |

### JWT vs Session

| 特性 | JWT | Session |
|------|-----|---------|
| **存储位置** | 客户端（localStorage） | 服务器（Redis/数据库） |
| **状态** | 无状态 | 有状态 |
| **扩展性** | ✅ 易扩展（分布式） | ⚠️ 需共享存储 |
| **安全性** | ⚠️ 无法主动失效 | ✅ 可立即失效 |
| **性能** | ✅ 无需查询数据库 | ⚠️ 每次请求查询 |
| **适用场景** | API、微服务 | 传统Web应用 |

---

## 🎓 学习建议

### 对于讲解者

1. **先讲概念**：用生活中的例子（银行卡、身份证）类比
2. **再讲流程**：画流程图，展示数据流动
3. **最后讲代码**：逐行解释关键代码
4. **动手演示**：
   - 在 [jwt.io](https://jwt.io/) 解码Token
   - 用Python演示Bcrypt加密
   - 用Postman测试API

### 对于学习者

1. **理解原理**：为什么需要认证？为什么选择JWT+Bcrypt？
2. **跟踪流程**：从登录到访问资源，Token如何传递？
3. **阅读代码**：对照文档阅读项目代码
4. **实践操作**：
   - 修改Token过期时间
   - 添加新的用户角色
   - 实现Token刷新机制

---

## 📚 参考资料

- **JWT官方文档**: https://jwt.io/
- **Bcrypt维基百科**: https://en.wikipedia.org/wiki/Bcrypt
- **FastAPI安全文档**: https://fastapi.tiangolo.com/tutorial/security/
- **OWASP密码存储指南**: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

---

**文档版本**: v1.0
**最后更新**: 2025-01-01
**作者**: 电厂巡检视频系统开发团队
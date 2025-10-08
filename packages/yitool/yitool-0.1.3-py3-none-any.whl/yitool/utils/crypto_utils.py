# -*- coding: utf-8 -*-
import hashlib
import base64
import hmac
import secrets
from typing import Union, Tuple, Optional


class CryptoUtils:
    """加密解密工具类"""
    
    @staticmethod
    def md5(data: Union[str, bytes]) -> str:
        """计算MD5哈希值
        
        Args:
            data: 要计算哈希的数据（字符串或字节）
        
        Returns:
            MD5哈希值（十六进制字符串）
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def sha1(data: Union[str, bytes]) -> str:
        """计算SHA1哈希值
        
        Args:
            data: 要计算哈希的数据（字符串或字节）
        
        Returns:
            SHA1哈希值（十六进制字符串）
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha1(data).hexdigest()
    
    @staticmethod
    def sha256(data: Union[str, bytes]) -> str:
        """计算SHA256哈希值
        
        Args:
            data: 要计算哈希的数据（字符串或字节）
        
        Returns:
            SHA256哈希值（十六进制字符串）
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def sha512(data: Union[str, bytes]) -> str:
        """计算SHA512哈希值
        
        Args:
            data: 要计算哈希的数据（字符串或字节）
        
        Returns:
            SHA512哈希值（十六进制字符串）
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha512(data).hexdigest()
    
    @staticmethod
    def hmac_md5(data: Union[str, bytes], key: Union[str, bytes]) -> str:
        """计算HMAC-MD5哈希值
        
        Args:
            data: 要计算哈希的数据（字符串或字节）
            key: 密钥（字符串或字节）
        
        Returns:
            HMAC-MD5哈希值（十六进制字符串）
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        return hmac.new(key, data, hashlib.md5).hexdigest()
    
    @staticmethod
    def hmac_sha256(data: Union[str, bytes], key: Union[str, bytes]) -> str:
        """计算HMAC-SHA256哈希值
        
        Args:
            data: 要计算哈希的数据（字符串或字节）
            key: 密钥（字符串或字节）
        
        Returns:
            HMAC-SHA256哈希值（十六进制字符串）
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        return hmac.new(key, data, hashlib.sha256).hexdigest()
    
    @staticmethod
    def base64_encode(data: Union[str, bytes]) -> str:
        """Base64编码
        
        Args:
            data: 要编码的数据（字符串或字节）
        
        Returns:
            Base64编码后的字符串
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def base64_decode(data: str) -> bytes:
        """Base64解码
        
        Args:
            data: Base64编码的字符串
        
        Returns:
            解码后的字节数据
        """
        return base64.b64decode(data)
    
    @staticmethod
    def base64_urlsafe_encode(data: Union[str, bytes]) -> str:
        """URL安全的Base64编码
        
        Args:
            data: 要编码的数据（字符串或字节）
        
        Returns:
            URL安全的Base64编码后的字符串
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.urlsafe_b64encode(data).decode('utf-8')
    
    @staticmethod
    def base64_urlsafe_decode(data: str) -> bytes:
        """URL安全的Base64解码
        
        Args:
            data: URL安全的Base64编码的字符串
        
        Returns:
            解码后的字节数据
        """
        return base64.urlsafe_b64decode(data)
    
    @staticmethod
    def generate_random_key(length: int = 32) -> bytes:
        """生成加密安全的随机密钥
        
        Args:
            length: 密钥长度（字节）
        
        Returns:
            随机密钥（字节）
        """
        return secrets.token_bytes(length)
    
    @staticmethod
    def generate_random_hex(length: int = 32) -> str:
        """生成加密安全的随机十六进制字符串
        
        Args:
            length: 字符串长度
        
        Returns:
            随机十六进制字符串
        """
        return secrets.token_hex(length // 2)
    
    @staticmethod
    def generate_random_str(length: int = 32) -> str:
        """生成加密安全的随机字符串
        
        Args:
            length: 字符串长度
        
        Returns:
            随机字符串
        """
        return secrets.token_urlsafe(length)[:length]
    
    @staticmethod
    def verify_hash(data: Union[str, bytes], hash_value: str, hash_type: str = 'sha256') -> bool:
        """验证数据的哈希值是否匹配
        
        Args:
            data: 要验证的数据（字符串或字节）
            hash_value: 要比较的哈希值
            hash_type: 哈希算法类型（md5, sha1, sha256, sha512）
        
        Returns:
            哈希值是否匹配
        
        Raises:
            ValueError: 如果哈希算法类型不支持
        """
        hash_functions = {
            'md5': CryptoUtils.md5,
            'sha1': CryptoUtils.sha1,
            'sha256': CryptoUtils.sha256,
            'sha512': CryptoUtils.sha512
        }
        
        if hash_type not in hash_functions:
            raise ValueError(f"不支持的哈希算法类型: {hash_type}")
        
        computed_hash = hash_functions[hash_type](data)
        return computed_hash.lower() == hash_value.lower()
    
    # 以下为更高级的加密功能，需要根据实际需求实现
    # 注意：生产环境使用前请确保进行充分的安全测试
    
    @staticmethod
    def aes_encrypt(data: Union[str, bytes], key: Union[str, bytes], 
                    iv: Optional[Union[str, bytes]] = None) -> Tuple[bytes, bytes]:
        """AES加密（高级功能，示例实现）
        
        注意：此方法仅为示例，生产环境请使用成熟的加密库
        
        Args:
            data: 要加密的数据
            key: 加密密钥
            iv: 初始化向量，如果为None则自动生成
        
        Returns:
            加密后的数据和使用的初始化向量
        """
        try:
            # 导入必要的库
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
            # 处理输入
            if isinstance(data, str):
                data = data.encode('utf-8')
            if isinstance(key, str):
                key = key.encode('utf-8')
            
            # 确保密钥长度正确
            key = key.ljust(32)[:32]  # 确保32字节（256位）
            
            # 生成初始化向量
            if iv is None:
                iv = secrets.token_bytes(16)  # AES块大小为16字节
            elif isinstance(iv, str):
                iv = iv.encode('utf-8')[:16].ljust(16, b'\0')
            else:
                iv = iv[:16].ljust(16, b'\0')
            
            # 填充数据（PKCS7）
            pad_length = 16 - (len(data) % 16)
            data = data + bytes([pad_length]) * pad_length
            
            # 创建加密器
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            # 加密数据
            encrypted_data = encryptor.update(data) + encryptor.finalize()
            
            return encrypted_data, iv
        except ImportError:
            raise ImportError("需要安装 cryptography 库: pip install cryptography")
    
    @staticmethod
    def aes_decrypt(encrypted_data: bytes, key: Union[str, bytes], iv: Union[str, bytes]) -> bytes:
        """AES解密（高级功能，示例实现）
        
        注意：此方法仅为示例，生产环境请使用成熟的加密库
        
        Args:
            encrypted_data: 加密后的数据
            key: 解密密钥
            iv: 初始化向量
        
        Returns:
            解密后的数据
        """
        try:
            # 导入必要的库
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
            # 处理输入
            if isinstance(key, str):
                key = key.encode('utf-8')
            if isinstance(iv, str):
                iv = iv.encode('utf-8')
            
            # 确保密钥和IV长度正确
            key = key.ljust(32)[:32]  # 确保32字节（256位）
            iv = iv[:16].ljust(16, b'\0')
            
            # 创建解密器
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            # 解密数据
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # 去除填充
            pad_length = decrypted_data[-1]
            decrypted_data = decrypted_data[:-pad_length]
            
            return decrypted_data
        except ImportError:
            raise ImportError("需要安装 cryptography 库: pip install cryptography")
    
    @staticmethod
    def generate_rsa_key_pair(key_size: int = 2048) -> Tuple[bytes, bytes]:
        """生成RSA密钥对（高级功能，示例实现）
        
        注意：此方法仅为示例，生产环境请使用成熟的加密库
        
        Args:
            key_size: 密钥大小（比特）
        
        Returns:
            私钥和公钥（PEM格式）
        """
        try:
            # 导入必要的库
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            
            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            
            # 序列化私钥（PEM格式）
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # 获取公钥
            public_key = private_key.public_key()
            
            # 序列化公钥（PEM格式）
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return private_pem, public_pem
        except ImportError:
            raise ImportError("需要安装 cryptography 库: pip install cryptography")
    
    @staticmethod
    def rsa_encrypt(data: Union[str, bytes], public_key_pem: bytes) -> bytes:
        """RSA加密（高级功能，示例实现）
        
        注意：此方法仅为示例，生产环境请使用成熟的加密库
        
        Args:
            data: 要加密的数据
            public_key_pem: PEM格式的公钥
        
        Returns:
            加密后的数据
        """
        try:
            # 导入必要的库
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            
            # 处理输入
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # 加载公钥
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=default_backend()
            )
            
            # 加密数据
            encrypted_data = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashlib.sha256()),
                    algorithm=hashlib.sha256(),
                    label=None
                )
            )
            
            return encrypted_data
        except ImportError:
            raise ImportError("需要安装 cryptography 库: pip install cryptography")
    
    @staticmethod
    def rsa_decrypt(encrypted_data: bytes, private_key_pem: bytes) -> bytes:
        """RSA解密（高级功能，示例实现）
        
        注意：此方法仅为示例，生产环境请使用成熟的加密库
        
        Args:
            encrypted_data: 加密后的数据
            private_key_pem: PEM格式的私钥
        
        Returns:
            解密后的数据
        """
        try:
            # 导入必要的库
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            
            # 加载私钥
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=default_backend()
            )
            
            # 解密数据
            decrypted_data = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashlib.sha256()),
                    algorithm=hashlib.sha256(),
                    label=None
                )
            )
            
            return decrypted_data
        except ImportError:
            raise ImportError("需要安装 cryptography 库: pip install cryptography")
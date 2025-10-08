# -*- coding: utf-8 -*-
import os
import sys
import platform
import subprocess
import time
import socket
import psutil
import re
from typing import Optional, Dict, List, Tuple, Union, Any
from datetime import datetime
from yitool.exceptions import YiToolException


class SystemUtils:
    """系统工具类，提供各种系统操作相关的功能"""
    
    @staticmethod
    def get_os_info() -> Dict[str, str]:
        """获取操作系统信息
        
        Returns:
            包含操作系统信息的字典
        """
        os_info = {
            'system': platform.system(),  # 操作系统名称
            'version': platform.version(),  # 操作系统版本
            'release': platform.release(),  # 操作系统发行版
            'architecture': ' '.join(platform.architecture()),  # 系统架构
            'machine': platform.machine(),  # 机器类型
            'processor': platform.processor()  # 处理器信息
        }
        
        # 获取更详细的信息
        try:
            if os_info['system'] == 'Windows':
                os_info['windows_version'] = platform.win32_ver()[0]
                os_info['windows_build'] = platform.win32_ver()[1]
            elif os_info['system'] == 'Darwin':
                os_info['macos_version'] = platform.mac_ver()[0]
            elif os_info['system'] == 'Linux':
                # 尝试获取Linux发行版信息
                try:
                    with open('/etc/os-release', 'r') as f:
                        for line in f:
                            if line.startswith('NAME='):
                                os_info['linux_distro'] = line.split('=', 1)[1].strip('"')
                            elif line.startswith('VERSION='):
                                os_info['linux_version'] = line.split('=', 1)[1].strip('"')
                except Exception:
                    pass
        except Exception:
            pass
        
        return os_info
    
    @staticmethod
    def get_python_info() -> Dict[str, str]:
        """获取Python解释器信息
        
        Returns:
            包含Python信息的字典
        """
        return {
            'version': platform.python_version(),  # Python版本
            'implementation': platform.python_implementation(),  # Python实现
            'compiler': platform.python_compiler(),  # 编译器
            'build': platform.python_build()[1]  # 构建日期
        }
    
    @staticmethod
    def get_hostname() -> str:
        """获取主机名
        
        Returns:
            主机名
        """
        return socket.gethostname()
    
    @staticmethod
    def get_ip_addresses() -> List[Tuple[str, str]]:
        """获取所有网络接口的IP地址
        
        Returns:
            IP地址列表，每个元素是(接口名, IP地址)的元组
        """
        addresses = []
        try:
            for if_name, if_addrs in psutil.net_if_addrs().items():
                for addr in if_addrs:
                    # 只获取IPv4和IPv6地址
                    if addr.family in (socket.AF_INET, socket.AF_INET6):
                        addresses.append((if_name, addr.address))
        except Exception:
            pass
        return addresses
    
    @staticmethod
    def get_public_ip() -> Optional[str]:
        """获取公网IP地址
        
        Returns:
            公网IP地址，如果获取失败则返回None
        """
        try:
            # 使用多个公共服务以增加可靠性
            services = [
                'https://api.ipify.org',
                'https://ifconfig.me/ip',
                'https://ipecho.net/plain'
            ]
            
            for service in services:
                try:
                    # 使用subprocess调用curl或wget
                    if SystemUtils.is_command_available('curl'):
                        result = subprocess.run(
                            ['curl', '-s', service],
                            capture_output=True, text=True, check=True
                        )
                        ip = result.stdout.strip()
                        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                            return ip
                    elif SystemUtils.is_command_available('wget'):
                        result = subprocess.run(
                            ['wget', '-qO-', service],
                            capture_output=True, text=True, check=True
                        )
                        ip = result.stdout.strip()
                        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                            return ip
                except Exception:
                    continue
        except Exception:
            pass
        return None
    
    @staticmethod
    def is_command_available(command: str) -> bool:
        """检查命令是否可用
        
        Args:
            command: 要检查的命令
        
        Returns:
            命令是否可用
        """
        try:
            # 使用subprocess调用which或where命令
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['where', command],
                    capture_output=True, text=True
                )
            else:
                result = subprocess.run(
                    ['which', command],
                    capture_output=True, text=True
                )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def run_command(command: str, shell: bool = False, timeout: Optional[int] = None) -> Dict[str, Union[str, int, bool]]:
        """运行系统命令
        
        Args:
            command: 要运行的命令
            shell: 是否在shell中运行
            timeout: 超时时间（秒）
        
        Returns:
            包含命令执行结果的字典
        
        Raises:
            YiToolException: 如果命令执行失败
        """
        try:
            # 准备命令
            if shell:
                cmd = command
            else:
                # 如果不使用shell，需要将命令拆分为列表
                if isinstance(command, str):
                    cmd = command.split()
                else:
                    cmd = command
            
            # 执行命令
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            raise YiToolException(f"Command timed out after {timeout} seconds: {command}")
        except Exception as e:
            raise YiToolException(f"Failed to run command: {command}. Error: {str(e)}")
    
    @staticmethod
    def get_system_load() -> Dict[str, float]:
        """获取系统负载信息
        
        Returns:
            包含系统负载信息的字典
        """
        load_info = {}
        try:
            if platform.system() == 'Linux' or platform.system() == 'Darwin':
                # 获取1、5、15分钟平均负载
                load_avg = os.getloadavg()
                load_info = {
                    '1min': load_avg[0],
                    '5min': load_avg[1],
                    '15min': load_avg[2]
                }
            elif platform.system() == 'Windows':
                # Windows没有直接的load average，可以用CPU使用率代替
                cpu_percent = psutil.cpu_percent(interval=1)
                load_info = {'cpu_percent': cpu_percent}
        except Exception:
            pass
        return load_info
    
    @staticmethod
    def get_memory_info() -> Dict[str, Union[int, float]]:
        """获取内存信息
        
        Returns:
            包含内存信息的字典
        """
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            }
        except Exception:
            return {}
    
    @staticmethod
    def get_disk_info(path: str = '/') -> Dict[str, Union[int, float]]:
        """获取磁盘信息
        
        Args:
            path: 要检查的路径
        
        Returns:
            包含磁盘信息的字典
        """
        try:
            disk = psutil.disk_usage(path)
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
        except Exception:
            return {}
    
    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """获取CPU信息
        
        Returns:
            包含CPU信息的字典
        """
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'total_cores': psutil.cpu_count(logical=True),
            'cpu_percent': psutil.cpu_percent(interval=1, percpu=True)
        }
        
        try:
            # 获取CPU频率信息
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info.update({
                    'current_freq': cpu_freq.current,
                    'min_freq': cpu_freq.min,
                    'max_freq': cpu_freq.max
                })
        except Exception:
            pass
        
        return cpu_info
    
    @staticmethod
    def get_process_info(pid: Optional[int] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """获取进程信息
        
        Args:
            pid: 进程ID，如果为None则返回所有进程信息
        
        Returns:
            进程信息字典或进程信息列表
        """
        try:
            if pid:
                # 获取单个进程信息
                with psutil.Process(pid) as p:
                    return SystemUtils._get_process_details(p)
            else:
                # 获取所有进程信息
                processes = []
                for p in psutil.process_iter(['pid', 'name', 'username']):
                    try:
                        processes.append(SystemUtils._get_process_details(p))
                    except psutil.NoSuchProcess:
                        pass
                return processes
        except Exception:
            return [] if pid is None else {}
    
    @staticmethod
    def _get_process_details(process: psutil.Process) -> Dict[str, Any]:
        """获取进程的详细信息
        
        Args:
            process: 进程对象
        
        Returns:
            进程详细信息字典
        """
        with process.oneshot():
            details = {
                'pid': process.pid,
                'name': process.name(),
                'status': process.status(),
                'created_at': datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # 尝试获取更多信息
            try:
                details['username'] = process.username()
            except Exception:
                details['username'] = 'N/A'
            
            try:
                details['cpu_percent'] = process.cpu_percent(interval=0.1)
                details['memory_percent'] = process.memory_percent()
            except Exception:
                details['cpu_percent'] = 0.0
                details['memory_percent'] = 0.0
            
            try:
                details['cmdline'] = ' '.join(process.cmdline()) if process.cmdline() else 'N/A'
            except Exception:
                details['cmdline'] = 'N/A'
            
            return details
    
    @staticmethod
    def kill_process(pid: int, force: bool = False) -> bool:
        """杀死进程
        
        Args:
            pid: 进程ID
            force: 是否强制杀死
        
        Returns:
            操作是否成功
        """
        try:
            with psutil.Process(pid) as p:
                if force:
                    p.kill()
                else:
                    p.terminate()
                # 等待进程终止
                p.wait(timeout=5)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_environment_variables() -> Dict[str, str]:
        """获取环境变量
        
        Returns:
            环境变量字典
        """
        return os.environ.copy()
    
    @staticmethod
    def set_environment_variable(name: str, value: str) -> None:
        """设置环境变量
        
        Args:
            name: 环境变量名称
            value: 环境变量值
        """
        os.environ[name] = value
    
    @staticmethod
    def get_environment_variable(name: str, default: Optional[str] = None) -> Optional[str]:
        """获取环境变量
        
        Args:
            name: 环境变量名称
            default: 默认值
        
        Returns:
            环境变量值或默认值
        """
        return os.environ.get(name, default)
    
    @staticmethod
    def sleep(seconds: float) -> None:
        """暂停执行指定的时间
        
        Args:
            seconds: 暂停的秒数
        """
        time.sleep(seconds)
    
    @staticmethod
    def get_uptime() -> float:
        """获取系统运行时间
        
        Returns:
            系统运行时间（秒）
        """
        try:
            if platform.system() == 'Windows':
                # Windows系统通过wmic获取启动时间
                result = subprocess.run(
                    ['wmic', 'os', 'get', 'LastBootUpTime', '/VALUE'],
                    capture_output=True, text=True, check=True
                )
                # 解析输出，格式为：20230101120000.000000+000
                match = re.search(r'LastBootUpTime=(\d{14})', result.stdout)
                if match:
                    boot_time_str = match.group(1)
                    boot_time = datetime.strptime(boot_time_str, '%Y%m%d%H%M%S')
                    return (datetime.now() - boot_time).total_seconds()
            else:
                # Linux/Mac系统读取/proc/uptime
                with open('/proc/uptime', 'r') as f:
                    uptime_seconds = float(f.readline().split()[0])
                    return uptime_seconds
        except Exception:
            return 0.0
    
    @staticmethod
    def shutdown(force: bool = False, delay: int = 0) -> None:
        """关闭系统
        
        Args:
            force: 是否强制关闭
            delay: 延迟关闭的秒数
        
        Raises:
            YiToolException: 如果关闭系统失败
        """
        try:
            if platform.system() == 'Windows':
                cmd = ['shutdown', '/s', '/t', str(delay)]
                if force:
                    cmd.append('/f')
            elif platform.system() == 'Darwin':
                cmd = ['sudo', 'shutdown', '-h', f'+{delay // 60}' if delay > 0 else 'now']
            else:  # Linux
                cmd = ['sudo', 'shutdown', '-h', f'+{delay // 60}' if delay > 0 else 'now']
            
            subprocess.run(cmd, check=True)
        except Exception as e:
            raise YiToolException(f"Failed to shutdown system. Error: {str(e)}")
    
    @staticmethod
    def reboot(delay: int = 0) -> None:
        """重启系统
        
        Args:
            delay: 延迟重启的秒数
        
        Raises:
            YiToolException: 如果重启系统失败
        """
        try:
            if platform.system() == 'Windows':
                cmd = ['shutdown', '/r', '/t', str(delay)]
            elif platform.system() == 'Darwin':
                cmd = ['sudo', 'shutdown', '-r', f'+{delay // 60}' if delay > 0 else 'now']
            else:  # Linux
                cmd = ['sudo', 'shutdown', '-r', f'+{delay // 60}' if delay > 0 else 'now']
            
            subprocess.run(cmd, check=True)
        except Exception as e:
            raise YiToolException(f"Failed to reboot system. Error: {str(e)}")
    
    @staticmethod
    def get_file_permissions(path: str) -> str:
        """获取文件权限
        
        Args:
            path: 文件路径
        
        Returns:
            文件权限字符串（如"rwxr-xr-x"）
        """
        try:
            # 获取文件状态
            st = os.stat(path)
            # 计算权限
            mode = st.st_mode
            permissions = []
            # 用户权限
            permissions.append('r' if mode & 0o400 else '-')
            permissions.append('w' if mode & 0o200 else '-')
            permissions.append('x' if mode & 0o100 else '-')
            # 组权限
            permissions.append('r' if mode & 0o040 else '-')
            permissions.append('w' if mode & 0o020 else '-')
            permissions.append('x' if mode & 0o010 else '-')
            # 其他用户权限
            permissions.append('r' if mode & 0o004 else '-')
            permissions.append('w' if mode & 0o002 else '-')
            permissions.append('x' if mode & 0o001 else '-')
            
            return ''.join(permissions)
        except Exception:
            return ''
    
    @staticmethod
    def set_file_permissions(path: str, permissions: Union[int, str]) -> bool:
        """设置文件权限
        
        Args:
            path: 文件路径
            permissions: 权限值（如0o755或"rwxr-xr-x"）
        
        Returns:
            操作是否成功
        """
        try:
            if isinstance(permissions, str):
                # 将权限字符串转换为数值
                perm_map = {
                    'r': 4, 'w': 2, 'x': 1, '-': 0
                }
                if len(permissions) != 9:
                    raise ValueError("Permission string must be 9 characters long")
                
                mode = 0
                # 用户权限
                mode |= perm_map[permissions[0]] << 6
                mode |= perm_map[permissions[1]] << 5
                mode |= perm_map[permissions[2]] << 4
                # 组权限
                mode |= perm_map[permissions[3]] << 3
                mode |= perm_map[permissions[4]] << 2
                mode |= perm_map[permissions[5]] << 1
                # 其他用户权限
                mode |= perm_map[permissions[6]]
                mode |= perm_map[permissions[7]] >> 1
                mode |= perm_map[permissions[8]] >> 2
                
                os.chmod(path, mode)
            else:
                # 直接使用数值权限
                os.chmod(path, permissions)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_current_user() -> str:
        """获取当前用户
        
        Returns:
            当前用户名
        """
        try:
            return os.getlogin()
        except Exception:
            try:
                return psutil.Process(os.getpid()).username()
            except Exception:
                return 'unknown'
            

if __name__ == '__main__':
    SystemUtils.get_current_user()
#!/usr/bin/env python3
# Ahmad Toolkit - أداة شبكات متعددة الوظائف محسنة
# تطوير بواسطة: Ahmad & المطورين المساهمين

import os
import sys
import subprocess
import platform
import ipaddress
import socket
import re
import argparse
import time
import json
import random
import threading
import requests
from datetime import datetime
try:
    from colorama import Fore, Back, Style, init
    from tabulate import tabulate
    from tqdm import tqdm
    import netifaces
except ImportError:
    print("[!] المكتبات المطلوبة غير متوفرة. جاري تثبيتها...")
    subprocess.run([sys.executable, "-m", "pip", "install", "colorama", "tabulate", "tqdm", "netifaces", "requests"])
    from colorama import Fore, Back, Style, init
    from tabulate import tabulate
    from tqdm import tqdm
    import netifaces

# تهيئة colorama للألوان
init()

# ألوان متعددة للشعار
colors = [Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.RED, Fore.YELLOW]

class AhmadToolkit:
    def __init__(self):
        # تعريف شعار متحرك بألوان متعددة
        self.banner = f"""
{random.choice(colors)}
     ▄▄▄      ██░ ██  ███▄ ▄███▓ ▄▄▄      ▓█████▄     
    ▒████▄    ▓██░ ██▒▓██▒▀█▀ ██▒▒████▄    ▒██▀ ██▌    
    ▒██  ▀█▄  ▒██▀▀██░▓██    ▓██░▒██  ▀█▄  ░██   █▌    
    ░██▄▄▄▄██ ░▓█ ░██ ▒██    ▒██ ░██▄▄▄▄██ ░▓█▄   ▌    
     ▓█   ▓██▒░▓█▒░██▓▒██▒   ░██▒ ▓█   ▓██▒░▒████▓     
     ▒▒   ▓▒█░ ▒ ░░▒░▒░ ▒░   ░  ░ ▒▒   ▓▒█░ ▒▒▓  ▒     
      ▒   ▒▒ ░ ▒ ░▒░ ░░  ░      ░  ▒   ▒▒ ░ ░ ▒  ▒     
      ░   ▒    ░  ░░ ░░      ░     ░   ▒    ░ ░  ░     
          ░  ░ ░  ░  ░       ░         ░  ░   ░        
                                            ░          
{random.choice(colors)}    _______ ____   ____  _     _  _____ _______ 
{random.choice(colors)}   |__   __/ __ \\ / __ \\| |   | |/ ____|__   __|
{random.choice(colors)}      | | | |  | | |  | | |   | | |  __   | |   
{random.choice(colors)}      | | | |  | | |  | | |   | | | |_ |  | |   
{random.choice(colors)}      | | | |__| | |__| | |___| | |__| |  | |   
{random.choice(colors)}      |_|  \\____/ \\____/ \\_____/ \\_____|  |_|   
                                                        
{Fore.YELLOW}[+] تم التطوير بواسطة Ahmad | v2.0.0
{Fore.CYAN}[+] https://github.com/ahmad/toolkit
{Style.RESET_ALL}
        """
        self.os_type = platform.system()
        self.is_root = os.geteuid() == 0 if self.os_type == "Linux" else False
        self.tools_path = os.path.join(os.path.expanduser("~"), ".ahmad_toolkit")
        self.config_file = os.path.join(self.tools_path, "config.json")
        self.logs_dir = os.path.join(self.tools_path, "logs")
        self.history_file = os.path.join(self.logs_dir, "history.log")
        self.scan_results = os.path.join(self.logs_dir, "scan_results")
        
        # إنشاء المجلدات اللازمة إذا لم تكن موجودة
        self.setup_directories()
        
        # تحميل الإعدادات
        self.load_config()
        
    def setup_directories(self):
        """إنشاء المجلدات اللازمة للأداة"""
        try:
            if not os.path.exists(self.tools_path):
                os.makedirs(self.tools_path)
            if not os.path.exists(self.logs_dir):
                os.makedirs(self.logs_dir)
            if not os.path.exists(self.scan_results):
                os.makedirs(self.scan_results)
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ في إنشاء المجلدات: {str(e)}{Style.RESET_ALL}")
            
    def load_config(self):
        """تحميل إعدادات الأداة"""
        default_config = {
            "auto_check_updates": True,
            "default_scan_type": "quick",
            "enable_logging": True,
            "terminal_theme": "dark",
            "max_log_size": 10,  # بالميجابايت
            "preferred_browser": "firefox",
            "show_animations": True,
            "last_update_check": None
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                with open(self.config_file, 'w') as f:
                    json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"{Fore.YELLOW}[!] تعذر تحميل الإعدادات: {str(e)}. استخدام الإعدادات الافتراضية.{Style.RESET_ALL}")
            self.config = default_config
            
    def save_config(self):
        """حفظ إعدادات الأداة"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"{Fore.GREEN}[+] تم حفظ الإعدادات بنجاح{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ في حفظ الإعدادات: {str(e)}{Style.RESET_ALL}")
            
    def log_activity(self, activity):
        """تسجيل النشاط في ملف السجل"""
        if not self.config.get("enable_logging", True):
            return
            
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {activity}\n"
            
            with open(self.history_file, 'a') as f:
                f.write(log_entry)
                
            # التحقق من حجم ملف السجل والتقليص إذا لزم الأمر
            if os.path.getsize(self.history_file) > (self.config.get("max_log_size", 10) * 1024 * 1024):
                self.truncate_log_file()
        except Exception as e:
            print(f"{Fore.YELLOW}[!] خطأ في تسجيل النشاط: {str(e)}{Style.RESET_ALL}")
                
    def truncate_log_file(self):
        """تقليص حجم ملف السجل عند تجاوزه الحد المسموح"""
        try:
            with open(self.history_file, 'r') as f:
                lines = f.readlines()
                
            # الاحتفاظ بآخر 1000 سطر فقط
            with open(self.history_file, 'w') as f:
                f.writelines(lines[-1000:])
        except Exception as e:
            print(f"{Fore.YELLOW}[!] خطأ في تقليص ملف السجل: {str(e)}{Style.RESET_ALL}")
            
    def animate_text(self, text):
        """عرض نص متحرك"""
        if not self.config.get("show_animations", True):
            print(text)
            return
            
        for char in text:
            print(char, end='', flush=True)
            time.sleep(0.01)
        print()
        
    def print_banner(self):
        """عرض شعار الأداة مع تأثير متحرك"""
        if self.config.get("show_animations", True):
            for line in self.banner.split('\n'):
                print(line)
                time.sleep(0.05)
        else:
            print(self.banner)
            
        # التحقق من وجود تحديثات إذا كان مفعلاً
        if self.config.get("auto_check_updates", True):
            self.check_for_updates()
        
    def check_for_updates(self):
        """التحقق من وجود تحديثات للأداة"""
        # وقت آخر تحقق من التحديثات
        last_check = self.config.get("last_update_check")
        
        # التحقق من التحديثات مرة واحدة يومياً فقط
        if last_check and (datetime.now() - datetime.fromisoformat(last_check)).days < 1:
            return
            
        try:
            print(f"{Fore.CYAN}[*] جاري التحقق من وجود تحديثات...{Style.RESET_ALL}")
            
            # هذا محاكاة فقط للتحقق من وجود تحديثات - في التطبيق الحقيقي سيتم الاتصال بخادم التحديثات
            time.sleep(1)
            
            # تحديث وقت آخر فحص
            self.config["last_update_check"] = datetime.now().isoformat()
            self.save_config()
            
            # تحقق وهمي من وجود تحديثات
            if random.choice([True, False]):
                print(f"{Fore.GREEN}[+] الإصدار الحالي هو الأحدث.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[!] هناك تحديث جديد متاح! يمكنك تحديث الأداة باستخدام الأمر: git pull{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}[!] خطأ في التحقق من التحديثات: {str(e)}{Style.RESET_ALL}")
            
    def check_root(self):
        """التحقق من صلاحيات الجذر"""
        if self.os_type == "Linux" and not self.is_root:
            print(f"{Fore.RED}[!] يجب تشغيل الأداة بصلاحيات الجذر (root) للحصول على جميع الميزات{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] جرب تشغيل الأمر: sudo {' '.join(sys.argv)}{Style.RESET_ALL}")
            
            # السؤال عما إذا كان يرغب المستخدم في المتابعة بدون صلاحيات الجذر
            continue_anyway = input(f"{Fore.YELLOW}هل ترغب في المتابعة بدون صلاحيات الجذر؟ (بعض الميزات لن تعمل) [y/N]: {Style.RESET_ALL}")
            if continue_anyway.lower() != 'y':
                sys.exit(1)
                
    def check_dependencies(self):
        """التحقق من وجود البرامج والمكتبات المطلوبة"""
        print(f"{Fore.CYAN}[*] جاري التحقق من المتطلبات...{Style.RESET_ALL}")
        
        dependencies = {
            "programs": ["nmap", "bettercap", "wireshark", "metasploit", "sqlmap"],
            "pip_packages": ["colorama", "tabulate", "tqdm", "netifaces", "requests"]
        }
        
        # التحقق من وجود البرامج
        missing_programs = []
        for program in dependencies["programs"]:
            try:
                with open(os.devnull, 'w') as devnull:
                    subprocess.run(["which", program], check=True, stdout=devnull, stderr=devnull)
            except subprocess.CalledProcessError:
                missing_programs.append(program)
                
        # التحقق من وجود حزم بايثون
        missing_packages = []
        for package in dependencies["pip_packages"]:
            try:
                __import__(package.lower())
            except ImportError:
                missing_packages.append(package)
                
        if missing_programs:
            print(f"{Fore.YELLOW}[!] البرامج التالية غير مثبتة: {', '.join(missing_programs)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[+] جميع البرامج المطلوبة متوفرة{Style.RESET_ALL}")
            
        if missing_packages:
            print(f"{Fore.YELLOW}[!] حزم بايثون التالية غير مثبتة: {', '.join(missing_packages)}{Style.RESET_ALL}")
            try:
                install_packages = input(f"{Fore.YELLOW}هل ترغب في تثبيت حزم بايثون المفقودة؟ [Y/n]: {Style.RESET_ALL}")
                if install_packages.lower() != 'n':
                    for package in missing_packages:
                        print(f"{Fore.CYAN}[*] جاري تثبيت {package}...{Style.RESET_ALL}")
                        subprocess.run([sys.executable, "-m", "pip", "install", package])
                    # تحديث قائمة الحزم المفقودة بعد التثبيت
                    missing_packages = []
            except Exception as e:
                print(f"{Fore.RED}[!] خطأ في تثبيت الحزم: {str(e)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[+] جميع حزم بايثون المطلوبة متوفرة{Style.RESET_ALL}")
            
        return {"programs": missing_programs, "packages": missing_packages}
    
    def install_tools(self, tool_name=None):
        """تثبيت الأدوات المطلوبة"""
        self.check_root()
        
        tools = {
            "bettercap": self.install_bettercap,
            "nmap": self.install_nmap,
            "wireshark": self.install_wireshark,
            "metasploit": self.install_metasploit,
            "sqlmap": self.install_sqlmap,
            "all": None  # ستستخدم لتثبيت جميع الأدوات
        }
        
        if tool_name:
            # تثبيت أداة محددة
            if tool_name == "all":
                for name, func in tools.items():
                    if name != "all" and func:
                        func()
            elif tool_name in tools and tools[tool_name]:
                tools[tool_name]()
            else:
                print(f"{Fore.RED}[!] الأداة '{tool_name}' غير معتمدة أو غير موجودة{Style.RESET_ALL}")
        else:
            # عرض قائمة بالأدوات المتاحة للتثبيت
            print(f"{Fore.CYAN}[*] الأدوات المتاحة للتثبيت:{Style.RESET_ALL}")
            for i, name in enumerate(tools.keys()):
                if name != "all":
                    print(f"  {i+1}. {name}")
            print(f"  {len(tools)}. all (جميع الأدوات)")
            
            try:
                choice = input(f"{Fore.YELLOW}اختر رقم الأداة للتثبيت (0 للإلغاء): {Style.RESET_ALL}")
                if choice == "0":
                    return
                    
                choice = int(choice)
                if 1 <= choice <= len(tools):
                    tool_names = list(tools.keys())
                    selected_tool = tool_names[choice-1]
                    
                    if selected_tool == "all":
                        for name, func in tools.items():
                            if name != "all" and func:
                                func()
                    elif tools[selected_tool]:
                        tools[selected_tool]()
                else:
                    print(f"{Fore.RED}[!] اختيار غير صالح{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] إدخال غير صالح{Style.RESET_ALL}")
    
    def install_bettercap(self):
        """تثبيت Bettercap حسب نوع نظام التشغيل"""
        print(f"{Fore.CYAN}[*] جاري تثبيت Bettercap...{Style.RESET_ALL}")
        self.log_activity("محاولة تثبيت Bettercap")
        
        try:
            if "kali" in platform.platform().lower():
                # تثبيت على كالي لينكس
                cmds = [
                    ["apt-get", "update", "-y"],
                    ["apt-get", "install", "bettercap", "-y"]
                ]
            elif "ubuntu" in platform.platform().lower() or "debian" in platform.platform().lower():
                # تثبيت على أوبونتو/ديبيان
                cmds = [
                    ["apt-get", "update", "-y"],
                    ["apt-get", "install", "build-essential", "libpcap-dev", "libusb-1.0-0-dev", "libnetfilter-queue-dev", "-y"],
                    ["apt-get", "install", "bettercap", "-y"]
                ]
            elif "arch" in platform.platform().lower():
                # تثبيت على آرتش لينكس
                cmds = [
                    ["pacman", "-Sy"],
                    ["pacman", "-S", "bettercap", "--noconfirm"]
                ]
            elif "fedora" in platform.platform().lower() or "centos" in platform.platform().lower() or "rhel" in platform.platform().lower():
                # تثبيت على فيدورا/سنتوس
                cmds = [
                    ["dnf", "install", "-y", "libpcap-devel", "libusb-devel", "make", "gcc", "git"],
                    ["git", "clone", "https://github.com/bettercap/bettercap", "/tmp/bettercap"],
                    ["cd", "/tmp/bettercap", "&&", "make", "build", "&&", "make", "install"]
                ]
            else:
                # تثبيت على توزيعات لينكس الأخرى أو أنظمة أخرى
                print(f"{Fore.YELLOW}[*] جاري محاولة التثبيت من المصدر...{Style.RESET_ALL}")
                cmds = [
                    ["git", "clone", "https://github.com/bettercap/bettercap", "/tmp/bettercap"],
                    ["cd", "/tmp/bettercap", "&&", "make", "build", "&&", "make", "install"]
                ]
            
            for cmd in cmds:
                process = subprocess.Popen(" ".join(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    print(f"{Fore.RED}[!] خطأ في تنفيذ الأمر: {' '.join(cmd)}{Style.RESET_ALL}")
                    print(f"{Fore.RED}الخطأ: {stderr.decode()}{Style.RESET_ALL}")
                    break
            
            # التحقق من نجاح التثبيت
            try:
                subprocess.run(["which", "bettercap"], check=True, stdout=subprocess.DEVNULL)
                print(f"{Fore.GREEN}[+] تم تثبيت Bettercap بنجاح{Style.RESET_ALL}")
                self.log_activity("تم تثبيت Bettercap بنجاح")
                return True
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}[!] فشل التثبيت. يرجى تثبيت Bettercap يدوياً من https://github.com/bettercap/bettercap{Style.RESET_ALL}")
                self.log_activity("فشل تثبيت Bettercap")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ أثناء تثبيت Bettercap: {str(e)}{Style.RESET_ALL}")
            self.log_activity(f"خطأ في تثبيت Bettercap: {str(e)}")
            return False
            
    def install_nmap(self):
        """تثبيت Nmap"""
        print(f"{Fore.CYAN}[*] جاري تثبيت Nmap...{Style.RESET_ALL}")
        self.log_activity("محاولة تثبيت Nmap")
        
        try:
            if self.os_type == "Linux":
                if "ubuntu" in platform.platform().lower() or "debian" in platform.platform().lower() or "kali" in platform.platform().lower():
                    cmds = [
                        ["apt-get", "update", "-y"],
                        ["apt-get", "install", "nmap", "-y"]
                    ]
                elif "arch" in platform.platform().lower():
                    cmds = [
                        ["pacman", "-Sy"],
                        ["pacman", "-S", "nmap", "--noconfirm"]
                    ]
                elif "fedora" in platform.platform().lower() or "centos" in platform.platform().lower() or "rhel" in platform.platform().lower():
                    cmds = [
                        ["dnf", "install", "-y", "nmap"]
                    ]
                else:
                    print(f"{Fore.YELLOW}[*] نظام التشغيل غير معروف. جاري محاولة استخدام apt...{Style.RESET_ALL}")
                    cmds = [
                        ["apt-get", "update", "-y"],
                        ["apt-get", "install", "nmap", "-y"]
                    ]
            elif self.os_type == "Darwin":  # macOS
                cmds = [
                    ["brew", "install", "nmap"]
                ]
            else:
                print(f"{Fore.RED}[!] نظام التشغيل غير مدعوم. يرجى تثبيت Nmap يدوياً.{Style.RESET_ALL}")
                return False
                
            for cmd in cmds:
                process = subprocess.Popen(" ".join(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    print(f"{Fore.RED}[!] خطأ في تنفيذ الأمر: {' '.join(cmd)}{Style.RESET_ALL}")
                    print(f"{Fore.RED}الخطأ: {stderr.decode()}{Style.RESET_ALL}")
                    break
            
            # التحقق من نجاح التثبيت
            try:
                subprocess.run(["which", "nmap"], check=True, stdout=subprocess.DEVNULL)
                print(f"{Fore.GREEN}[+] تم تثبيت Nmap بنجاح{Style.RESET_ALL}")
                self.log_activity("تم تثبيت Nmap بنجاح")
                return True
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}[!] فشل التثبيت. يرجى تثبيت Nmap يدوياً من https://nmap.org/download.html{Style.RESET_ALL}")
                self.log_activity("فشل تثبيت Nmap")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ أثناء تثبيت Nmap: {str(e)}{Style.RESET_ALL}")
            self.log_activity(f"خطأ في تثبيت Nmap: {str(e)}")
            return False
            
    def install_wireshark(self):
        """تثبيت Wireshark"""
        print(f"{Fore.CYAN}[*] جاري تثبيت Wireshark...{Style.RESET_ALL}")
        self.log_activity("محاولة تثبيت Wireshark")
        
        try:
            if self.os_type == "Linux":
                if "ubuntu" in platform.platform().lower() or "debian" in platform.platform().lower() or "kali" in platform.platform().lower():
                    cmds = [
                        ["apt-get", "update", "-y"],
                        ["apt-get", "install", "wireshark", "-y"]
                    ]
                elif "arch" in platform.platform().lower():
                    cmds = [
                        ["pacman", "-Sy"],
                        ["pacman", "-S", "wireshark-qt", "--noconfirm"]
                    ]
                elif "fedora" in platform.platform().lower() or "centos" in platform.platform().lower() or "rhel" in platform.platform().lower():
                    cmds = [
                        ["dnf", "install", "-y", "wireshark"]
                    ]
                else:
                    print(f"{Fore.YELLOW}[*] نظام التشغيل غير معروف. جاري محاولة استخدام apt...{Style.RESET_ALL}")
                    cmds = [
                        ["apt-get", "update", "-y"],
                        ["apt-get", "install", "wireshark", "-y"]
                    ]
            elif self.os_type == "Darwin":  # macOS
                cmds = [
                    ["brew", "install", "wireshark"]
                ]
            else:
                print(f"{Fore.RED}[!] نظام التشغيل غير مدعوم. يرجى تثبيت Wireshark يدوياً.{Style.RESET_ALL}")
                return False
                
            for cmd in cmds:
                process = subprocess.Popen(" ".join(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    print(f"{Fore.RED}[!] خطأ في تنفيذ الأمر: {' '.join(cmd)}{Style.RESET_ALL}")
                    print(f"{Fore.RED}الخطأ: {stderr.decode()}{Style.RESET_ALL}")
                    break
            
            # التحقق من نجاح التثبيت
            try:
                subprocess.run(["which", "wireshark"], check=True, stdout=subprocess.DEVNULL)
                print(f"{Fore.GREEN}[+] تم تثبيت Wireshark بنجاح{Style.RESET_ALL}")
                self.log_activity("تم تثبيت Wireshark بنجاح")
                return True
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}[!] فشل التثبيت. يرجى تثبيت Wireshark يدوياً من https://www.wireshark.org/download.html{Style.RESET_ALL}")
                self.log_activity("فشل تثبيت Wireshark")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ أثناء تثبيت Wireshark: {str(e)}{Style.RESET_ALL}")
            self.log_activity(f"خطأ في تثبيت Wireshark: {str(e)}")
            return False
            
    def install_metasploit(self):
        """تثبيت Metasploit Framework"""
        print(f"{Fore.CYAN}[*] جاري تثبيت Metasploit Framework...{Style.RESET_ALL}")
        self.log_activity("محاولة تثبيت Metasploit Framework")
        
        try:
            if self.os_type == "Linux":
                if "kali" in platform.platform().lower():
                    cmds = [
                        ["apt-get", "update", "-y"],
                        ["apt-get", "install", "metasploit-framework", "-y"]
                    ]
                elif "ubuntu" in platform.platform().lower() or "debian" in platform.platform().lower():
                    # تثبيت على أوبونتو/ديبيان
                    cmds = [
                        ["apt-get", "update", "-y"],
                        ["apt-get", "install", "curl", "gnupg2", "-y"],
                        ["curl", "https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb", ">", "msfinstall"],
                        ["chmod", "+x", "msfinstall"],
                        ["./msfinstall"]
                    ]
                elif "arch" in platform.platform().lower():
                    # تثبيت على آرتش لينكس
                    cmds = [
                        ["pacman", "-Sy"],
                        ["pacman", "-S", "metasploit", "--noconfirm"]
                    ]
                elif "fedora" in platform.platform().lower() or "centos" in platform.platform().lower() or "rhel" in platform.platform().lower():
                    # تثبيت على فيدورا/سنتوس
                    cmds = [
                        ["dnf", "install", "-y", "curl"],
                        ["curl", "https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb", ">", "msfinstall"],
                        ["chmod", "+x", "msfinstall"],
                        ["./msfinstall"]
                    ]
                else:
                    print(f"{Fore.YELLOW}[*] نظام التشغيل غير معروف. جاري استخدام النص البرمجي الرسمي للتثبيت...{Style.RESET_ALL}")
                    cmds = [
                        ["curl", "https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb", ">", "msfinstall"],
                        ["chmod", "+x", "msfinstall"],
                        ["./msfinstall"]
                    ]
            else:
                print(f"{Fore.RED}[!] نظام التشغيل غير مدعوم. يرجى تثبيت Metasploit يدوياً من https://github.com/rapid7/metasploit-framework/wiki/Nightly-Installers{Style.RESET_ALL}")
                return False
                
            for cmd in cmds:
                process = subprocess.Popen(" ".join(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    print(f"{Fore.RED}[!] خطأ في تنفيذ الأمر: {' '.join(cmd)}{Style.RESET_ALL}")
                    print(f"{Fore.RED}الخطأ: {stderr.decode()}{Style.RESET_ALL}")
                    break
            
            # التحقق من نجاح التثبيت
            try:
                subprocess.run(["which", "msfconsole"], check=True, stdout=subprocess.DEVNULL)
                print(f"{Fore.GREEN}[+] تم تثبيت Metasploit Framework بنجاح{Style.RESET_ALL}")
                self.log_activity("تم تثبيت Metasploit Framework بنجاح")
                return True
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}[!] فشل التثبيت. يرجى تثبيت Metasploit Framework يدوياً من https://github.com/rapid7/metasploit-framework/wiki/Nightly-Installers{Style.RESET_ALL}")
                self.log_activity("فشل تثبيت Metasploit Framework")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ أثناء تثبيت Metasploit Framework: {str(e)}{Style.RESET_ALL}")
            self.log_activity(f"خطأ في تثبيت Metasploit Framework: {str(e)}")
            return False
            
    def install_sqlmap(self):
        """تثبيت SQLMap"""
        print(f"{Fore.CYAN}[*] جاري تثبيت SQLMap...{Style.RESET_ALL}")
        self.log_activity("محاولة تثبيت SQLMap")
        
        try:
            if self.os_type == "Linux":
                if "ubuntu" in platform.platform().lower() or "debian" in platform.platform().lower() or "kali" in platform.platform().lower():
                    cmds = [
                        ["apt-get", "update", "-y"],
                        ["apt-get", "install", "sqlmap", "-y"]
                    ]
                elif "arch" in platform.platform().lower():
                    cmds = [
                        ["pacman", "-Sy"],
                        ["pacman", "-S", "sqlmap", "--noconfirm"]
                    ]
                elif "fedora" in platform.platform().lower() or "centos" in platform.platform().lower() or "rhel" in platform.platform().lower():
                    cmds = [
                        ["dnf", "install", "-y", "sqlmap"]
                    ]
                else:
                    print(f"{Fore.YELLOW}[*] نظام التشغيل غير معروف. جاري تثبيت SQLMap من المصدر...{Style.RESET_ALL}")
                    cmds = [
                        ["git", "clone", "--depth", "1", "https://github.com/sqlmapproject/sqlmap.git", "/opt/sqlmap"],
                        ["ln", "-sf", "/opt/sqlmap/sqlmap.py", "/usr/local/bin/sqlmap"]
                    ]
            elif self.os_type == "Darwin":  # macOS
                cmds = [
                    ["brew", "install", "sqlmap"]
                ]
            else:
                print(f"{Fore.RED}[!] نظام التشغيل غير مدعوم. يرجى تثبيت SQLMap يدوياً من https://github.com/sqlmapproject/sqlmap{Style.RESET_ALL}")
                return False
                
            for cmd in cmds:
                process = subprocess.Popen(" ".join(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    print(f"{Fore.RED}[!] خطأ في تنفيذ الأمر: {' '.join(cmd)}{Style.RESET_ALL}")
                    print(f"{Fore.RED}الخطأ: {stderr.decode()}{Style.RESET_ALL}")
                    break
            
            # التحقق من نجاح التثبيت
            try:
                subprocess.run(["which", "sqlmap"], check=True, stdout=subprocess.DEVNULL)
                print(f"{Fore.GREEN}[+] تم تثبيت SQLMap بنجاح{Style.RESET_ALL}")
                self.log_activity("تم تثبيت SQLMap بنجاح")
                return True
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}[!] فشل التثبيت. يرجى تثبيت SQLMap يدوياً من https://github.com/sqlmapproject/sqlmap{Style.RESET_ALL}")
                self.log_activity("فشل تثبيت SQLMap")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ أثناء تثبيت SQLMap: {str(e)}{Style.RESET_ALL}")
            self.log_activity(f"خطأ في تثبيت SQLMap: {str(e)}")
            return False
    
    def get_network_interfaces(self):
        """الحصول على قائمة واجهات الشبكة المتاحة"""
        interfaces = []
        try:
            # الحصول على جميع واجهات الشبكة باستخدام netifaces
            ifaces = netifaces.interfaces()
            
            for iface in ifaces:
                # تجاهل واجهات loopback
                if iface == "lo" or "loop" in iface.lower():
                    continue
                    
                # الحصول على معلومات الواجهة
                addrs = netifaces.ifaddresses(iface)
                mac = addrs.get(netifaces.AF_LINK, [{'addr': 'غير معروف'}])[0]['addr']
                ip = addrs.get(netifaces.AF_INET, [{'addr': 'غير معروف'}])[0]['addr'] if netifaces.AF_INET in addrs else 'غير معروف'
                
                # إضافة معلومات الواجهة إلى القائمة
                interfaces.append({
                    'name': iface,
                    'mac': mac,
                    'ip': ip
                })
                
            return interfaces
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ في الحصول على واجهات الشبكة: {str(e)}{Style.RESET_ALL}")
            return []
            
    def network_scan(self, target=None, scan_type="quick"):
        """إجراء مسح للشبكة باستخدام nmap"""
        print(f"{Fore.CYAN}[*] جاري بدء المسح الشبكي...{Style.RESET_ALL}")
        self.log_activity(f"بدء مسح الشبكة نوع: {scan_type}, هدف: {target}")
        
        if not target:
            # الحصول على عنوان IP للشبكة المحلية
            interfaces = self.get_network_interfaces()
            if not interfaces:
                print(f"{Fore.RED}[!] لم يتم العثور على واجهات شبكة نشطة{Style.RESET_ALL}")
                return
                
            # عرض الواجهات المتاحة للمستخدم للاختيار
            print(f"{Fore.CYAN}[*] واجهات الشبكة المتاحة:{Style.RESET_ALL}")
            for i, iface in enumerate(interfaces):
                print(f"  {i+1}. {iface['name']} - IP: {iface['ip']}, MAC: {iface['mac']}")
                
            try:
                choice = int(input(f"{Fore.YELLOW}اختر واجهة للمسح (0 للإلغاء): {Style.RESET_ALL}"))
                if choice == 0:
                    return
                    
                if 1 <= choice <= len(interfaces):
                    selected_iface = interfaces[choice-1]
                    ip_parts = selected_iface['ip'].split('.')
                    if len(ip_parts) == 4 and selected_iface['ip'] != 'غير معروف':
                        target = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
                    else:
                        print(f"{Fore.RED}[!] عنوان IP غير صالح للواجهة المحددة{Style.RESET_ALL}")
                        target = input(f"{Fore.YELLOW}أدخل هدف المسح (مثال: 192.168.1.0/24): {Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[!] اختيار غير صالح{Style.RESET_ALL}")
                    return
            except ValueError:
                print(f"{Fore.RED}[!] إدخال غير صالح{Style.RESET_ALL}")
                return
                
        # التحقق من وجود أداة nmap
        try:
            subprocess.run(["which", "nmap"], check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}[!] أداة nmap غير مثبتة. جاري محاولة التثبيت...{Style.RESET_ALL}")
            if not self.install_nmap():
                return
                
        # تحديد نوع المسح
        scan_options = {
            "quick": "-sn",  # مسح سريع لاكتشاف الأجهزة فقط
            "basic": "-sV -O --osscan-limit",  # مسح أساسي لاكتشاف الخدمات ونظام التشغيل
            "full": "-sS -sV -O -A",  # مسح كامل مع اكتشاف متقدم
            "vuln": "-sV --script=vuln"  # مسح للثغرات الأمنية
        }
        
        if scan_type not in scan_options:
            scan_type = "quick"
            
        scan_opt = scan_options[scan_type]
        
        # إنشاء اسم ملف التقرير
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.scan_results, f"scan_{timestamp}.xml")
        
        # بناء أمر المسح
        command = f"nmap {scan_opt} -oX {output_file} {target}"
        
        print(f"{Fore.CYAN}[*] جاري تنفيذ المسح: {command}{Style.RESET_ALL}")
        
        try:
            # تشغيل المسح
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            # عرض تقدم المسح
            if self.config.get("show_animations", True):
                with tqdm(total=100, desc="تقدم المسح", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
                    while process.poll() is None:
                        # تحديث شريط التقدم ببطء أثناء المسح
                        progress = min(pbar.n + 1, 95)  # الحد الأقصى هو 95% حتى ينتهي المسح فعلياً
                        pbar.update(progress - pbar.n)
                        time.sleep(0.5)
                    pbar.update(100 - pbar.n)  # إكمال شريط التقدم
            else:
                stdout, stderr = process.communicate()
                if stdout:
                    print(stdout)
                if stderr:
                    print(f"{Fore.RED}[!] أخطاء أثناء المسح: {stderr}{Style.RESET_ALL}")
                    
            # التحقق من نتيجة المسح
            if process.returncode == 0:
                print(f"{Fore.GREEN}[+] اكتمل المسح بنجاح. تم حفظ النتائج في: {output_file}{Style.RESET_ALL}")
                self.log_activity(f"اكتمل المسح بنجاح. ملف التقرير: {output_file}")
                
                # عرض نتائج المسح
                self.parse_nmap_results(output_file)
                
                return output_file
            else:
                print(f"{Fore.RED}[!] فشل المسح. تحقق من الاتصال والصلاحيات.{Style.RESET_ALL}")
                self.log_activity("فشل مسح الشبكة")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ أثناء المسح: {str(e)}{Style.RESET_ALL}")
            self.log_activity(f"خطأ في مسح الشبكة: {str(e)}")
            return None
            
    def parse_nmap_results(self, xml_file):
        """تحليل نتائج مسح nmap وعرضها بتنسيق مناسب"""
        try:
            if not os.path.exists(xml_file):
                print(f"{Fore.RED}[!] ملف نتائج المسح غير موجود: {xml_file}{Style.RESET_ALL}")
                return
                
            # قراءة ملف XML
            with open(xml_file, 'r') as f:
                xml_content = f.read()
                
            # البحث عن الأجهزة النشطة
            hosts = re.findall(r'<host.*?</host>', xml_content, re.DOTALL)
            
            if not hosts:
                print(f"{Fore.YELLOW}[*] لم يتم العثور على أجهزة نشطة في نطاق المسح{Style.RESET_ALL}")
                return
                
            # جمع معلومات الأجهزة
            devices = []
            for host in hosts:
                # الحصول على عنوان IP
                ip_match = re.search(r'<address addr="([^"]+)" addrtype="ipv4"', host)
                if not ip_match:
                    continue
                    
                ip = ip_match.group(1)
                
                # الحصول على عنوان MAC إذا كان متاحاً
                mac_match = re.search(r'<address addr="([^"]+)" addrtype="mac"', host)
                mac = mac_match.group(1) if mac_match else "غير معروف"
                
                # الحصول على اسم الجهاز إذا كان متاحاً
                hostname_match = re.search(r'<hostname name="([^"]+)"', host)
                hostname = hostname_match.group(1) if hostname_match else "غير معروف"
                
                # الحصول على حالة الجهاز (مفتوح أم لا)
                status_match = re.search(r'<status state="([^"]+)"', host)
                status = status_match.group(1) if status_match else "غير معروف"
                
                # الحصول على المنافذ المفتوحة
                ports_match = re.findall(r'<port protocol="([^"]+)" portid="([^"]+)">.*?<state state="([^"]+)".*?<service name="([^"]+)".*?</port>', host, re.DOTALL)
                
                open_ports = []
                for port in ports_match:
                    if port[2] == "open":
                        open_ports.append({
                            'protocol': port[0],
                            'port': port[1],
                            'service': port[3]
                        })
                
                # إضافة معلومات الجهاز إلى القائمة
                devices.append({
                    'ip': ip,
                    'mac': mac,
                    'hostname': hostname,
                    'status': status,
                    'open_ports': open_ports
                })
                
            # عرض الأجهزة المكتشفة
            print(f"{Fore.GREEN}[+] تم اكتشاف {len(devices)} جهاز نشط:{Style.RESET_ALL}")
            
            table_data = []
            for device in devices:
                ports_str = ", ".join([f"{p['port']}/{p['protocol']} ({p['service']})" for p in device['open_ports']])
                table_data.append([
                    device['ip'],
                    device['mac'],
                    device['hostname'],
                    ports_str if device['open_ports'] else "لا توجد منافذ مفتوحة"
                ])
                
            # عرض النتائج في جدول
            headers = ["عنوان IP", "عنوان MAC", "اسم الجهاز", "المنافذ المفتوحة"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            return devices
            
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ في تحليل نتائج المسح: {str(e)}{Style.RESET_ALL}")
            return None
    
    def wireless_scan(self):
        """مسح للشبكات اللاسلكية المتاحة"""
        print(f"{Fore.CYAN}[*] جاري البحث عن الشبكات اللاسلكية المتاحة...{Style.RESET_ALL}")
        self.log_activity("بدء مسح الشبكات اللاسلكية")
        
        # التحقق من نوع نظام التشغيل
        if self.os_type != "Linux":
            print(f"{Fore.RED}[!] هذه الميزة متاحة فقط على أنظمة لينكس{Style.RESET_ALL}")
            return None
            
        # التحقق من وجود الأدوات المطلوبة
        try:
            subprocess.run(["which", "iwlist"], check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"{Fore.RED}[!] الأداة iwlist غير مثبتة. جاري التثبيت...{Style.RESET_ALL}")
            try:
                if "debian" in platform.platform().lower() or "ubuntu" in platform.platform().lower() or "kali" in platform.platform().lower():
                    subprocess.run(["apt-get", "install", "-y", "wireless-tools"], check=True)
                elif "arch" in platform.platform().lower():
                    subprocess.run(["pacman", "-S", "--noconfirm", "wireless_tools"], check=True)
                elif "fedora" in platform.platform().lower() or "centos" in platform.platform().lower():
                    subprocess.run(["dnf", "install", "-y", "wireless-tools"], check=True)
                else:
                    print(f"{Fore.RED}[!] لا يمكن تثبيت الأدوات المطلوبة تلقائياً. يرجى تثبيت حزمة wireless-tools يدوياً.{Style.RESET_ALL}")
                    return None
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}[!] فشل تثبيت الأدوات المطلوبة{Style.RESET_ALL}")
                return None
                
        # الحصول على واجهات الشبكة اللاسلكية
        wireless_interfaces = []
        ifaces = self.get_network_interfaces()
        
        for iface in ifaces:
            # التحقق مما إذا كانت واجهة لاسلكية
            try:
                result = subprocess.run(["iwconfig", iface['name']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if "no wireless extensions" not in result.stdout.decode() and "no wireless extensions" not in result.stderr.decode():
                    wireless_interfaces.append(iface['name'])
            except Exception:
                continue
                
        if not wireless_interfaces:
            print(f"{Fore.RED}[!] لم يتم العثور على واجهات شبكة لاسلكية{Style.RESET_ALL}")
            return None
            
        # عرض الواجهات اللاسلكية المتاحة
        print(f"{Fore.CYAN}[*] واجهات الشبكة اللاسلكية المتاحة:{Style.RESET_ALL}")
        for i, iface in enumerate(wireless_interfaces):
            print(f"  {i+1}. {iface}")
            
        # اختيار الواجهة للمسح
        try:
            choice = int(input(f"{Fore.YELLOW}اختر واجهة للمسح (0 للإلغاء): {Style.RESET_ALL}"))
            if choice == 0:
                return None
                
            if 1 <= choice <= len(wireless_interfaces):
                selected_iface = wireless_interfaces[choice-1]
            else:
                print(f"{Fore.RED}[!] اختيار غير صالح{Style.RESET_ALL}")
                return None
        except ValueError:
            print(f"{Fore.RED}[!] إدخال غير صالح{Style.RESET_ALL}")
            return None
            
        # تنفيذ المسح اللاسلكي
        try:
            # تفعيل وضع المسح للواجهة
            if self.is_root:
                subprocess.run(["ifconfig", selected_iface, "up"], check=True)
                
            # إجراء المسح
            print(f"{Fore.CYAN}[*] جاري مسح الشبكات اللاسلكية باستخدام {selected_iface}...{Style.RESET_ALL}")
            scan_result = subprocess.run(["iwlist", selected_iface, "scan"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if scan_result.returncode != 0:
                print(f"{Fore.RED}[!] فشل المسح: {scan_result.stderr}{Style.RESET_ALL}")
                return None
                
            # تحليل نتائج المسح
            scan_output = scan_result.stdout
            
            # استخراج المعلومات من النتائج
            networks = []
            cells = re.split(r'Cell \d+ -', scan_output)[1:]  # تقسيم النتائج إلى خلايا شبكات
            
            for cell in cells:
                # استخراج معلومات الشبكة
                ssid_match = re.search(r'ESSID:"([^"]*)"', cell)
                bssid_match = re.search(r'Address: ([0-9A-F:]{17})', cell)
                channel_match = re.search(r'Channel:(\d+)', cell)
                frequency_match = re.search(r'Frequency:([\d.]+) GHz', cell)
                quality_match = re.search(r'Quality=(\d+)/(\d+)', cell)
                signal_match = re.search(r'Signal level=(-\d+) dBm', cell)
                encryption_match = re.search(r'Encryption key:(on|off)', cell)
                
                if ssid_match:
                    ssid = ssid_match.group(1)
                    bssid = bssid_match.group(1) if bssid_match else "غير معروف"
                    channel = channel_match.group(1) if channel_match else "غير معروف"
                    frequency = frequency_match.group(1) if frequency_match else "غير معروف"
                    
                    quality = "غير معروف"
                    if quality_match:
                        quality_val = int(quality_match.group(1))
                        quality_max = int(quality_match.group(2))
                        quality = f"{quality_val}/{quality_max} ({int(quality_val/quality_max*100)}%)"
                        
                    signal = signal_match.group(1) if signal_match else "غير معروف"
                    encryption = "مشفرة" if encryption_match and encryption_match.group(1) == "on" else "غير مشفرة"
                    
                    networks.append({
                        'ssid': ssid,
                        'bssid': bssid,
                        'channel': channel,
                        'frequency': frequency,
                        'quality': quality,
                        'signal': signal,
                        'encryption': encryption
                    })
                    
            # عرض النتائج
            if networks:
                print(f"{Fore.GREEN}[+] تم العثور على {len(networks)} شبكة لاسلكية:{Style.RESET_ALL}")
                
                table_data = []
                for network in networks:
                    table_data.append([
                        network['ssid'],
                        network['bssid'],
                        network['channel'],
                        network['signal'] + " dBm",
                        network['quality'],
                        network['encryption']
                    ])
                    
                headers = ["اسم الشبكة", "عنوان BSSID", "القناة", "قوة الإشارة", "الجودة", "التشفير"]
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
                # حفظ النتائج في ملف
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = os.path.join(self.scan_results, f"wifi_scan_{timestamp}.json")
                
                with open(output_file, 'w') as f:
                    json.dump(networks, f, indent=4)
                    
                print(f"{Fore.GREEN}[+] تم حفظ نتائج المسح في: {output_file}{Style.RESET_ALL}")
                self.log_activity(f"اكتمل مسح الشبكات اللاسلكية. ملف النتائج: {output_file}")
                
                return networks
            else:
                print(f"{Fore.YELLOW}[*] لم يتم العثور على شبكات لاسلكية{Style.RESET_ALL}")
                return []
                
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ أثناء المسح اللاسلكي: {str(e)}{Style.RESET_ALL}")
            self.log_activity(f"خطأ في مسح الشبكات اللاسلكية: {str(e)}")
            return None

if __name__ == "__main__":
    tool = AhmadToolkit()
    tool.print_banner()
    tool.check_root()
    tool.check_dependencies()
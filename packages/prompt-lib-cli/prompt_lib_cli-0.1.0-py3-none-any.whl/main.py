#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
import argparse
import pyperclip
import editor

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit
from prompt_toolkit.widgets import Box, Label, TextArea, Dialog, Button
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import input_dialog, message_dialog, yes_no_dialog
from prompt_toolkit.application import run_in_terminal

__version__ = "0.1.0"

class PromptLibrary:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "prompt-lib"
        self.data_file = self.config_dir / "prompt.json"
        self.ensure_config_dir()
    
    def ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self.save_prompts({})
    
    def load_prompts(self):
        """加载 prompts 数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_prompts(self, prompts):
        """保存 prompts 数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
    
    def add_prompt(self, name, content):
        """添加新的 prompt"""
        prompts = self.load_prompts()
        if name in prompts:
            print(f"错误: Prompt '{name}' 已存在")
            return False
        prompts[name] = content
        self.save_prompts(prompts)
        print(f"已添加 prompt: {name}")
        return True
    
    def delete_prompt(self, name):
        """删除 prompt"""
        prompts = self.load_prompts()
        if name in prompts:
            del prompts[name]
            self.save_prompts(prompts)
            return True
        return False
    
    def rename_prompt(self, old_name, new_name):
        """重命名 prompt"""
        prompts = self.load_prompts()
        if old_name in prompts and new_name not in prompts:
            prompts[new_name] = prompts.pop(old_name)
            self.save_prompts(prompts)
            return True
        return False
    
    def update_prompt(self, name, content):
        """更新 prompt 内容"""
        prompts = self.load_prompts()
        if name in prompts:
            prompts[name] = content
            self.save_prompts(prompts)
            return True
        return False

class InteractiveList:
    def __init__(self, library):
        self.library = library
        self.current_index = 0
        self.prompts = []
        self.refresh_prompts()
        
        # 创建按键绑定
        self.kb = KeyBindings()
        self.setup_key_bindings()
        
        # 创建界面组件
        self.title_label = Label("Prompt Library - 使用方向键选择，回车查看，r重命名，d删除，e编辑，q退出")
        self.list_area = TextArea(focusable=False, read_only=True)
        self.status_label = Label("")
        
        self.update_list_display()
        
        # 布局
        self.layout = Layout(
            HSplit([
                self.title_label,
                Box(self.list_area, padding=1),
                self.status_label
            ])
        )
        
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            mouse_support=True,
            full_screen=True
        )
    
    def refresh_prompts(self):
        """刷新 prompts 列表"""
        prompts_dict = self.library.load_prompts()
        self.prompts = list(prompts_dict.keys())
        self.prompts.sort()
    
    def update_list_display(self):
        """更新列表显示"""
        if not self.prompts:
            self.list_area.text = "没有保存的 prompts"
            return
        
        lines = []
        for i, name in enumerate(self.prompts):
            if i == self.current_index:
                lines.append(f"> {name}")
            else:
                lines.append(f"  {name}")
        
        self.list_area.text = "\n".join(lines)
    
    def setup_key_bindings(self):
        """设置按键绑定"""
        
        @self.kb.add('up')
        def _(event):
            if self.prompts:
                self.current_index = max(0, self.current_index - 1)
                self.update_list_display()
        
        @self.kb.add('down')
        def _(event):
            if self.prompts:
                self.current_index = min(len(self.prompts) - 1, self.current_index + 1)
                self.update_list_display()
        
        @self.kb.add('enter')
        def _(event):
            if self.prompts:
                self.show_prompt_content()
        
        @self.kb.add('r')
        def _(event):
            if self.prompts:
                self.rename_current_prompt()
        
        @self.kb.add('d')
        def _(event):
            if self.prompts:
                self.delete_current_prompt()
        
        @self.kb.add('e')
        def _(event):
            if self.prompts:
                self.edit_current_prompt()
        
        @self.kb.add('q')
        def _(event):
            event.app.exit()
    
    def get_current_prompt_name(self):
        """获取当前选中的 prompt 名称"""
        if self.prompts and 0 <= self.current_index < len(self.prompts):
            return self.prompts[self.current_index]
        return None
    
    def show_prompt_content(self):
        """显示并复制 prompt 内容"""
        name = self.get_current_prompt_name()
        if not name:
            return
        
        prompts = self.library.load_prompts()
        content = prompts.get(name, "")
        
        # 复制到剪贴板
        try:
            pyperclip.copy(content)
            self.status_label.text = f"已复制 '{name}' 到剪贴板"
        except Exception as e:
            self.status_label.text = f"复制到剪贴板失败: {e}"
        
        # 使用 run_in_terminal 来显示内容
        def _show_content():
            print(f"\n=== {name} ===")
            print(content)
            print("\n按 Enter 返回...")
            input()
        
        # 临时退出应用显示内容
        self.app.exit(result=_show_content)
    
    def rename_current_prompt(self):
        """重命名当前选中的 prompt"""
        old_name = self.get_current_prompt_name()
        if not old_name:
            return
        
        def _rename():
            new_name = input(f"请输入新的名称 (当前: {old_name}): ").strip()
            if new_name and new_name != old_name:
                if self.library.rename_prompt(old_name, new_name):
                    self.refresh_prompts()
                    # 找到新名称的位置
                    if new_name in self.prompts:
                        self.current_index = self.prompts.index(new_name)
                    self.update_list_display()
                    self.status_label.text = f"已重命名 '{old_name}' 为 '{new_name}'"
                else:
                    self.status_label.text = f"重命名失败: '{new_name}' 已存在或原名称不存在"
            else:
                self.status_label.text = "重命名已取消"
        
        self.app.exit(result=_rename)
    
    def delete_current_prompt(self):
        """删除当前选中的 prompt"""
        name = self.get_current_prompt_name()
        if not name:
            return
        
        def _delete():
            response = input(f"确定要删除 '{name}' 吗? (y/N): ").strip().lower()
            if response == 'y':
                if self.library.delete_prompt(name):
                    self.refresh_prompts()
                    if self.current_index >= len(self.prompts) and self.prompts:
                        self.current_index = len(self.prompts) - 1
                    self.update_list_display()
                    self.status_label.text = f"已删除 '{name}'"
                else:
                    self.status_label.text = f"删除失败: '{name}' 不存在"
            else:
                self.status_label.text = "删除已取消"
        
        self.app.exit(result=_delete)
    
    def edit_current_prompt(self):
        """编辑当前选中的 prompt"""
        name = self.get_current_prompt_name()
        if not name:
            return
        
        prompts = self.library.load_prompts()
        current_content = prompts.get(name, "")
        
        def _edit():
            try:
                # 使用默认编辑器编辑内容
                new_content = editor.editor(current_content)
                if new_content is not None:
                    # editor 返回的是 bytes，需要解码
                    if isinstance(new_content, bytes):
                        new_content = new_content.decode('utf-8')
                    # 移除可能的末尾换行符
                    new_content = new_content.rstrip('\n\r')
                    
                    if self.library.update_prompt(name, new_content):
                        self.status_label.text = f"已更新 '{name}'"
                    else:
                        self.status_label.text = f"更新失败: '{name}' 不存在"
                else:
                    self.status_label.text = "编辑已取消"
            except Exception as e:
                self.status_label.text = f"编辑失败: {e}"
        
        self.app.exit(result=_edit)
    
    def run(self):
        """运行交互式列表"""
        if not self.prompts:
            print("没有保存的 prompts，使用 'add' 命令添加一些吧！")
            return
        
        try:
            while True:
                result = self.app.run()
                if callable(result):
                    # 执行回调函数
                    result()
                    # 刷新显示
                    self.update_list_display()
                else:
                    break
        except KeyboardInterrupt:
            print("\n已退出")

def main():
    parser = argparse.ArgumentParser(description="Prompt Library CLI")
    parser.add_argument("-v", "--version", action="store_true", help="显示版本信息")

    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加新的 prompt')
    add_parser.add_argument('name', help='prompt 名称')
    add_parser.add_argument('content', help='prompt 内容')
    
    # ls 命令
    subparsers.add_parser('ls', help='列出所有 prompts')
    
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return 0
    
    library = PromptLibrary()
    
    if args.command == 'add':
        library.add_prompt(args.name, args.content)
    elif args.command == 'ls':
        interactive_list = InteractiveList(library)
        interactive_list.run()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
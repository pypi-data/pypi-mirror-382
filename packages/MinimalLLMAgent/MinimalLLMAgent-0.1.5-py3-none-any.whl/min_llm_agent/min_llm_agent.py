import os
import json
import csv
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Union, List
from openai import OpenAI
from LyPythonToolbox import lyprint_separator, overwrite_stdout


supported_platform_name_list = ["OpenAI", "Grok", "DeepSeek", "Gemini", "Ali"]

api_key_envname_dict = {
    "OpenAI": "OPENAI_API_KEY",
    "Grok": "XAI_API_KEY",
    "DeepSeek": "DEEPSEEK_API_KEY",
    "Gemini": "GEMINI_API_KEY",
    "Ali": "DASHSCOPE_API_KEY",
}

base_url_envname_dict = {
    "OpenAI": "OPENAI_BASE_URL",
    "Grok": "XAI_BASE_URL",
    "DeepSeek": "DEEPSEEK_BASE_URL",
    "Gemini": "GEMINI_BASE_URL",
    "Ali": "DASHSCOPE_BASE_URL",
}

INTERACTIVE_HELP_STR = """
- To submit a query: start a new line, type '/', and press Enter.
    - Line breaks are allowed and recognized as a part of the query.
- Query 'q' or 'Q' to exit.
- Query 'm' or 'M' to print the memory.

See more details on: 
- Homepage: https://github.com/YueLin301/min_llm_agent
- GitHub Page: https://github.com/YueLin301/min_llm_agent
- PyPI Page: https://pypi.org/project/MinimalLLMAgent/
"""


def init_client(platform_name=None, model_name=None):
    if platform_name is None:
        if model_name is None:
            raise ValueError("Either platform_name or model_name must be provided")

        for platform in supported_platform_name_list:
            try:
                client = OpenAI(
                    api_key=os.getenv(api_key_envname_dict[platform]),
                    base_url=os.getenv(base_url_envname_dict[platform]),
                )
                check_result = client.models.list()

                for model in check_result.data:
                    if model.id == model_name:
                        return client, platform
            except Exception:
                continue

        raise ValueError(
            f"Model '{model_name}' not found in any accessible platform. Please check the model name or provide platform_name explicitly."
        )
    else:
        assert (
            platform_name in supported_platform_name_list
        ), f"Invalid platform name: {platform_name}\nAvailable platforms: {supported_platform_name_list}"

        client = OpenAI(
            api_key=os.getenv(api_key_envname_dict[platform_name]),
            base_url=os.getenv(base_url_envname_dict[platform_name]),
        )

        return client, platform_name


def print_all_supported_platforms():
    lyprint_separator()
    print(f"Supported platforms: {supported_platform_name_list}")


def print_accessible_models(platform_name, id_only=True):
    assert platform_name in supported_platform_name_list, f"Platform {platform_name} is not supported"

    lyprint_separator()
    print(f"Available models for platform {platform_name}:")

    client, _ = init_client(platform_name)
    check_result = client.models.list()

    for model in check_result.data:
        if id_only:
            print(model.id)
        else:
            print(model)
        # print(model)


def print_all_supported_accessible_models(id_only=True):
    # all api keys are needed.
    for platform_name in supported_platform_name_list:
        print_accessible_models(platform_name, id_only)


class min_llm_agent_class:
    def __init__(self, model_name: str = "gpt-4o-mini", platform_name: str = None, name: str = "Yue's minimal LLM agent"):
        self.model_name = model_name
        self.name = name
        self.memory = []
        self.client, self.platform_name = init_client(platform_name, model_name)
        
        # GUI configuration constants
        self.default_font_size = 12
        self.default_font_family = "TkDefaultFont"  # Cross-platform font
        self.button_padding = {"padx": 20, "pady": 5}
        self.frame_padding = {"padx": 5, "pady": 5}
        self.window_size = "1000x700"

    def messages_preprocess(self, messages_raw: Union[str, List[dict]], role: str = "user"):
        assert role in ["user", "system"], f"Invalid role: {role}\nAvailable roles: {['user', 'system']}"

        if isinstance(messages_raw, str):
            messages = [
                {
                    "role": role,
                    "content": messages_raw,
                }
            ]
        elif isinstance(messages_raw, list) and all(isinstance(item, dict) for item in messages_raw):
            messages = messages_raw
        else:
            raise ValueError(f"Invalid input: {messages_raw}\nAvailable types: {str, list[dict]}")

        return messages

    # @lyprint_elapsed_time
    def vanilla_query(self, messages: List[dict], **kwargs):
        assert isinstance(messages, list) and all(
            isinstance(item, dict) for item in messages
        ), f"Invalid input: {messages}\nAvailable types: {list[dict]}"

        try:
            output_full = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs,
            )
        except Exception as e:
            raise e

        output_text = output_full.choices[0].message.content

        return output_text

    def add_anwer_to_memory(self, answer: str):
        self.memory = self.memory + [
            {
                "role": "assistant",
                "content": answer,
            }
        ]

    def reset_memory(self):
        self.memory = []

    def get_memory(self):
        return self.memory

    def set_memory(self, memory: List[dict]):
        self.memory = memory

    def append_memory(self, memory_new: dict):
        self.memory.append(memory_new)

    def print_memory(self, memory_item_separator: str = None):
        lyprint_separator("=")
        print("Memory:")
        lyprint_separator("-")
        for i, message in enumerate(self.memory):
            role_i = message["role"]
            content_i = message["content"]
            print(f"""[{i}] ({role_i}): {content_i}""")
            if memory_item_separator is not None:
                assert isinstance(memory_item_separator, str), f"Invalid memory item separator: {memory_item_separator}\nAvailable types: {str}"
                lyprint_separator(memory_item_separator)
        if memory_item_separator is not None:
            overwrite_stdout(1)
        lyprint_separator("=")

    def __call__(self, messages_raw: Union[str, List[dict]], role: str = "user", with_memory: bool = True, **kwargs):

        messages = self.messages_preprocess(messages_raw, role)

        if with_memory:
            self.memory = self.memory + messages
            messages = self.memory

        answer = self.vanilla_query(messages, **kwargs)

        if with_memory:
            self.add_anwer_to_memory(answer)

        return answer

    def interact_terminal(self):
        lyprint_separator()

        print(f"""\nThis is {self.name}, powered by the model "{self.model_name}".\n{INTERACTIVE_HELP_STR}""")

        time_step = 0
        while True:
            lyprint_separator(">")

            print(f"[{time_step}] Question:")
            question_lines = []
            first_question_line = True
            while True:
                line = input("> " if first_question_line else "")
                if line.strip().upper() == "/":
                    break
                question_lines.append(line)
                first_question_line = False

            question = "\n".join(question_lines)

            # ================================

            if question.strip().upper() == "Q":
                break
            elif question.strip().upper() == "M":
                self.print_memory()
                continue

            # ================================

            print("")
            lyprint_separator("<")
            print("Querying...")

            response = self(question, role="user")

            overwrite_stdout(1)
            output_print_str = f"[{time_step}] Answer by the model {self.model_name}:"
            print(output_print_str)
            # print("-" * len(output_print_str))
            print(response)
            print("\n")
            time_step += 1

    def interact_GUI(self):
        self.root = tk.Tk()
        self.root.title(f"{self.name} - {self.model_name}")
        self.root.geometry(self.window_size)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        memory_frame = self._create_label_frame(self.root, "Memory")
        memory_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2))
        memory_frame.grid_rowconfigure(0, weight=1)
        memory_frame.grid_rowconfigure(1, weight=0)
        memory_frame.grid_columnconfigure(0, weight=1)

        self.memory_edit_text = self._create_text_widget(memory_frame, wrap=tk.NONE, state=tk.DISABLED)
        self.memory_edit_text.grid(row=0, column=0, sticky="nsew", **self.frame_padding)

        memory_buttons_frame = tk.Frame(memory_frame)
        memory_buttons_frame.grid(row=1, column=0, sticky="ew", **self.frame_padding)
        
        memory_buttons_config = [
            ("Import Memory", self._import_memory_csv),
            ("Export Memory", self._export_memory_csv),
            ("Clear Memory", self._clear_memory_from_main)
        ]
        self._create_button_grid(memory_buttons_frame, memory_buttons_config)

        interaction_frame = self._create_label_frame(self.root, "Interaction")
        interaction_frame.grid(row=0, column=1, sticky="nsew", padx=2)
        interaction_frame.grid_rowconfigure(0, weight=1)
        interaction_frame.grid_rowconfigure(1, weight=0)
        interaction_frame.grid_rowconfigure(2, weight=0)
        interaction_frame.grid_columnconfigure(0, weight=1)

        self.conversation_text = self._create_text_widget(interaction_frame, wrap=tk.NONE, state=tk.DISABLED)
        self.conversation_text.grid(row=0, column=0, sticky="nsew", **self.frame_padding)

        font_buttons_frame = tk.Frame(interaction_frame)
        font_buttons_frame.grid(row=1, column=0, sticky="ew", **self.frame_padding)
        
        font_buttons_config = [
            ("Decrease Font", self._decrease_font_size),
            ("Reset Default", self._reset_font_size),
            ("Increase Font", self._increase_font_size)
        ]
        self._create_button_grid(font_buttons_frame, font_buttons_config)

        display_buttons_frame = tk.Frame(interaction_frame)
        display_buttons_frame.grid(row=2, column=0, sticky="ew", **self.frame_padding)
        
        display_buttons_config = [
            ("Show Memory", self._show_memory_in_conversation),
            ("Clear Display", self._clear_conversation_display)
        ]
        self._create_button_grid(display_buttons_frame, display_buttons_config)

        self.conversation_text.tag_configure("user", foreground="black", font=self._get_font(bold=True))
        self.conversation_text.tag_configure("assistant", foreground="black", font=self._get_font(bold=True))
        self.conversation_text.tag_configure("system", foreground="black", font=self._get_font())

        input_frame = self._create_label_frame(self.root, "Input")
        input_frame.grid(row=0, column=2, sticky="nsew", padx=(2, 5))
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_rowconfigure(1, weight=0)
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_text = tk.Text(input_frame, wrap=tk.WORD, font=self._get_font(), relief=tk.SUNKEN, bd=2)
        self.input_text.grid(row=0, column=0, sticky="nsew", **self.frame_padding)

        send_button_frame = tk.Frame(input_frame)
        send_button_frame.grid(row=1, column=0, sticky="ew", **self.frame_padding)

        send_button = self._create_button(send_button_frame, "Send Query", self._send_query)
        send_button.pack(expand=True, fill=tk.X)

        self.input_text.bind("<Control-Return>", lambda e: self._send_query())
        self.input_text.bind("<Return>", lambda e: self._send_query() if not self.input_text.get("1.0", "end-1c").strip() else None)

        self.conversation_count = 0
        self.font_size = self.default_font_size

        self._load_memory_to_display()
        self._add_to_conversation("system", "[Tip: Press \"Send Query\" or Ctrl+Enter to submit.]")

        self.root.mainloop()

    def _get_font(self, size=None, bold=False):
        if size is None:
            size = self.default_font_size
        if bold:
            return (self.default_font_family, size, "bold")
        return (self.default_font_family, size)

    def _create_button(self, parent, text, command, **kwargs):
        default_kwargs = {
            "font": self._get_font(),
            "relief": tk.RAISED,
            **self.button_padding
        }
        default_kwargs.update(kwargs)
        return tk.Button(parent, text=text, command=command, **default_kwargs)

    def _create_label_frame(self, parent, text, **kwargs):
        default_kwargs = {
            "font": self._get_font(bold=True),
            **self.frame_padding
        }
        default_kwargs.update(kwargs)
        return tk.LabelFrame(parent, text=text, **default_kwargs)

    def _create_text_widget(self, parent, **kwargs):
        default_kwargs = {
            "font": self._get_font(),
            **self.frame_padding
        }
        default_kwargs.update(kwargs)
        return scrolledtext.ScrolledText(parent, **default_kwargs)

    def _create_button_grid(self, parent, buttons_config, row=0):
        for i in range(len(buttons_config)):
            parent.grid_columnconfigure(i, weight=1)
        
        for i, (text, command) in enumerate(buttons_config):
            button = self._create_button(parent, text, command)
            if i == 0:
                button.grid(row=row, column=i, sticky="ew", padx=(0, 1))
            elif i == len(buttons_config) - 1:
                button.grid(row=row, column=i, sticky="ew", padx=(1, 0))
            else:
                button.grid(row=row, column=i, sticky="ew", padx=1)

    def _send_query(self):
        query = self.input_text.get("1.0", "end-1c").strip()

        if not query:
            messagebox.showwarning("Empty Query", "Please enter a question before sending.")
            return

        self.input_text.delete("1.0", tk.END)
        self._add_to_conversation("user", query)
        self.root.title(f"{self.name} - {self.model_name} - Querying...")
        self.input_text.config(state=tk.DISABLED)

        import threading
        query_thread = threading.Thread(target=self._process_query_async, args=(query,))
        query_thread.daemon = True
        query_thread.start()

    def _process_query_async(self, query):
        try:
            response = self(query, role="user", with_memory=True)
            self.conversation_text.after(0, self._update_conversation_after_query, response)
        except Exception as e:
            self.conversation_text.after(0, self._handle_query_error, str(e))

    def _update_conversation_after_query(self, response):
        self.root.title(f"{self.name} - {self.model_name}")
        self._add_to_conversation("assistant", response)
        self.conversation_count += 1
        self._load_memory_to_display()
        self.input_text.config(state=tk.NORMAL)
        self.input_text.focus()

    def _handle_query_error(self, error_msg):
        self.root.title(f"{self.name} - {self.model_name}")
        self._add_to_conversation("system", f"[Error: {error_msg}]")
        messagebox.showerror("Query Error", f"An error occurred while processing your query:\n{error_msg}")
        self.input_text.config(state=tk.NORMAL)
        self.input_text.focus()

    def _print_separator(self, char="-", length=80):
        return char * length

    def _load_memory_to_display(self):
        memory = self.get_memory()
        self.memory_edit_text.config(state=tk.NORMAL)
        self.memory_edit_text.delete("1.0", tk.END)
        if memory:
            memory_text = ""
            for i, message in enumerate(memory):
                role = message["role"]
                content = message["content"]
                memory_text += f"{self._print_separator("-")}\n\n[{i}] {role}:\n{content}\n\n"
            self.memory_edit_text.insert(tk.END, memory_text)
        else:
            self.memory_edit_text.insert(tk.END, "[Info: Memory is empty.]")
        self.memory_edit_text.config(state=tk.DISABLED)


    def _clear_memory_from_main(self):
        result = messagebox.askyesno("Clear Memory", "Are you sure you want to clear the memory? This action cannot be undone.")
        
        if result:
            self.reset_memory()
            self._load_memory_to_display()
            self._add_to_conversation("system", "[Info: Memory has been cleared.]")
            messagebox.showinfo("Memory Cleared", "Memory has been successfully cleared.")

    def _show_memory(self):
        memory = self.get_memory()

        if not memory:
            messagebox.showinfo("Memory", "Memory is empty.")
            return

        memory_window = tk.Toplevel()
        memory_window.title("Memory Contents")
        memory_window.geometry("600x400")

        memory_text = scrolledtext.ScrolledText(memory_window, wrap=tk.WORD, font=("Arial", 10), state=tk.DISABLED)
        memory_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        memory_text.config(state=tk.NORMAL)
        memory_text.insert(tk.END, "Current Memory:\n" + "=" * 50 + "\n\n")

        for i, message in enumerate(memory):
            role = message["role"]
            content = message["content"]
            memory_text.insert(tk.END, f"[{i}] ({role}): {content}\n\n")

        memory_text.config(state=tk.DISABLED)

    def _clear_memory(self):
        result = messagebox.askyesno("Clear Memory", "Are you sure you want to clear the memory? This action cannot be undone.")

        if result:
            self.reset_memory()
            self._add_to_conversation("system", "Memory has been cleared.")
            messagebox.showinfo("Memory Cleared", "Memory has been successfully cleared.")

    def _add_to_conversation(self, role, content):
        self.conversation_text.config(state=tk.NORMAL)
        
        current_count = self.conversation_count if role != "system" else ""
        
        if role == "system":
            separator = self._print_separator("=")
            full_content = f"{separator}\n{content}\n\n"
            self.conversation_text.insert(tk.END, full_content)
        else:
            formatted_content = f"{self._print_separator("-")}\n\n[{current_count}] {role}:\n{content}\n\n"
            self.conversation_text.insert(tk.END, formatted_content)

        if role == "user":
            lines = self.conversation_text.get("1.0", tk.END).split('\n')
            for i, line in enumerate(lines):
                if line.startswith(f"[{current_count}] {role}:"):
                    line_num = i + 1
                    self.conversation_text.tag_add("user", f"{line_num}.0", f"{line_num}.end")
                    break
        elif role == "assistant":
            lines = self.conversation_text.get("1.0", tk.END).split('\n')
            for i, line in enumerate(lines):
                if line.startswith(f"[{current_count}] {role}:"):
                    line_num = i + 1
                    self.conversation_text.tag_add("assistant", f"{line_num}.0", f"{line_num}.end")
                    break
        elif role == "system":
            self.conversation_text.tag_add("system", "end-3l", "end-2l")

        self.conversation_text.see(tk.END)
        self.conversation_text.config(state=tk.DISABLED)

    def _import_memory_csv(self):
        file_path = filedialog.askopenfilename(
            title="Import Memory",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            imported_memory = []
            with open(file_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                
                # Check if required columns exist
                if 'role' not in csv_reader.fieldnames or 'content' not in csv_reader.fieldnames:
                    raise ValueError("CSV file must contain 'role' and 'content' columns")
                
                for row in csv_reader:
                    role = row['role'].strip()
                    content = row['content'].strip()
                    
                    if not role or not content:
                        continue  # Skip empty rows
                    
                    if role not in ['user', 'assistant', 'system']:
                        raise ValueError(f"Invalid role '{role}'. Role must be 'user', 'assistant', or 'system'")
                    
                    imported_memory.append({
                        "role": role,
                        "content": content
                    })
            
            if not imported_memory:
                messagebox.showwarning("Import Warning", "No valid memory entries found in the CSV file.")
                return
            
            # Ask user if they want to replace or append
            result = messagebox.askyesnocancel(
                "Import Memory", 
                f"Do you want to replace current memory with {len(imported_memory)} imported memory items?\n\n"
                "Yes: Replace current memory\n"
                "No: Append to current memory\n"
                "Cancel: Cancel import"
            )
            
            if result is None:  # Cancel
                return
            elif result:  # Replace
                self.set_memory(imported_memory)
                self._add_to_conversation("system", f"Memory replaced with {len(imported_memory)} memory items from CSV file.")
            else:  # Append
                for message in imported_memory:
                    self.append_memory(message)
                self._add_to_conversation("system", f"Appended {len(imported_memory)} memory items to current memory.")
            
            # Update memory display
            self._load_memory_to_display()
            
            messagebox.showinfo("Import Successful", f"Successfully imported {len(imported_memory)} memory items from CSV file.")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import memory:\n{str(e)}")

    def _export_memory_csv(self):
        memory = self.get_memory()
        
        if not memory:
            messagebox.showwarning("Export Memory", "Memory is empty. Nothing to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Memory",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                csv_writer = csv.writer(f)
                
                # Write header
                csv_writer.writerow(['role', 'content'])
                
                # Write memory data
                for message in memory:
                    csv_writer.writerow([message['role'], message['content']])
            
            self._add_to_conversation("system", f"Memory exported to {file_path} ({len(memory)} memory items).")
            messagebox.showinfo("Export Successful", f"Memory successfully exported to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export memory:\n{str(e)}")




    def _decrease_font_size(self):
        if self.font_size > 6:  # Minimum font size
            self.font_size -= 1
            self._update_all_fonts()

    def _increase_font_size(self):
        if self.font_size < 20:  # Maximum font size
            self.font_size += 1
            self._update_all_fonts()

    def _reset_font_size(self):
        self.font_size = self.default_font_size
        self._update_all_fonts()

    def _update_all_fonts(self):
        self.memory_edit_text.config(font=self._get_font(self.font_size))
        self.conversation_text.config(font=self._get_font(self.font_size))
        self.input_text.config(font=self._get_font(self.font_size))
        
        self.conversation_text.tag_configure("user", foreground="black", font=self._get_font(self.font_size, bold=True))
        self.conversation_text.tag_configure("assistant", foreground="black", font=self._get_font(self.font_size, bold=True))
        self.conversation_text.tag_configure("system", foreground="black", font=self._get_font(self.font_size))

    def _show_memory_in_conversation(self):
        memory = self.get_memory()
        
        self.conversation_text.config(state=tk.NORMAL)
        
        if not memory:
            # Add simple empty memory message
            separator = self._print_separator("=")
            content = f"{separator}\n[Info: Memory is empty.]\n\n"
            self.conversation_text.insert(tk.END, content)
        else:
            # Add memory header with = separator
            separator = self._print_separator("=")
            header = f"{separator}\nCurrent Memory ({len(memory)} memory items):\n"
            self.conversation_text.insert(tk.END, header)
            
            # Add each memory item with same format as memory display
            for i, message in enumerate(memory):
                role = message["role"]
                content = message["content"]
                # Format: [index] role:\ncontent\n\n-separator\n\n
                memory_item = f"{self._print_separator('-')}\n\n[{i}] {role}:\n{content}\n\n"
                self.conversation_text.insert(tk.END, memory_item)

            # Add final = separator
            final_separator = f"{self._print_separator('=')}\n\n"
            self.conversation_text.insert(tk.END, final_separator)

        
        # Auto-scroll to bottom
        self.conversation_text.see(tk.END)
        self.conversation_text.config(state=tk.DISABLED)

    def _clear_conversation_display(self):
        result = messagebox.askyesno("Clear Display", "Are you sure you want to clear the conversation display? This action cannot be undone.")
        
        if result:
            self.conversation_text.config(state=tk.NORMAL)
            self.conversation_text.delete("1.0", tk.END)
            self.conversation_text.config(state=tk.DISABLED)
            
            # Reset conversation count
            self.conversation_count = 0
            
            # Add tip message
            self._add_to_conversation("system", "[Tip: Press \"Send Query\" or Ctrl+Enter to submit.]")
            
            messagebox.showinfo("Display Cleared", "Conversation display has been successfully cleared.")

    def interact(self, mode: str = "GUI"):
        if mode == "terminal":
            self.interact_terminal()
        elif mode == "GUI":
            self.interact_GUI()
        else:
            raise ValueError(f"Invalid mode: {mode}\nAvailable modes: {['terminal', 'GUI']}")


if __name__ == "__main__":
    agent = min_llm_agent_class()
    agent.interact(mode="GUI")
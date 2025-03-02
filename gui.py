import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import multiprocessing
from handler import process_queue, input_cleaner
from writer import write_to_queue
import json

def load_profiles():
    """Load profile names from the 'profiles' directory and append the 'Edit Profiles' option."""
    defaults_dir = os.path.join("profiles","defaults")
    profiles_dir = "profiles"

    if not os.path.exists(profiles_dir):
        os.makedirs(profiles_dir)
    
    if not os.path.exists(defaults_dir):
            os.makedirs(defaults_dir)

    default_profiles = [os.path.splitext(f)[0] for f in os.listdir(defaults_dir) if os.path.isfile(os.path.join(defaults_dir, f))]
    user_profiles = [os.path.splitext(f)[0] for f in os.listdir(profiles_dir) if os.path.isfile(os.path.join(profiles_dir, f))]

    profiles = default_profiles + user_profiles + ["Edit Profiles..."]  # Combine profiles with special option
    return profiles


def open_json_table_editor(profile_name, profile_path, data):
    """Opens a window with a table to edit only 'keywords' and 'keymap'."""
    editor_window = tk.Toplevel(tk_root)
    editor_window.title(f"Editing {profile_name}")
    editor_window.geometry("600x400")

    tk.Label(editor_window, text=f"Editing: {profile_name}", font=("Arial", 12)).pack(pady=5)

    # Extract the 'keywords' section from JSON
    keywords_data = data.get("keywords", [])

    # Frame for adding new keywords
    add_frame = tk.Frame(editor_window)
    add_frame.pack(pady=5, fill="x")

    tk.Label(add_frame, text="Keyword:").pack(side="left")
    keyword_entry = tk.Entry(add_frame)
    keyword_entry.pack(side="left", padx=5)

    tk.Label(add_frame, text="Keymap:").pack(side="left")
    keymap_entry = tk.Entry(add_frame, width=40)
    keymap_entry.pack(side="left", padx=5)

    def add_new_entry():
        """Adds a new keyword-keymap pair to the table."""
        new_keyword = input_cleaner(keyword_entry.get())
        new_keymap = keymap_entry.get().strip()

        if new_keyword and new_keymap:
            try:
                new_keymap_list = eval(new_keymap)  # Convert string input to a list
                if isinstance(new_keymap_list, list):
                    tree.insert("", "end", values=(new_keyword, str(new_keymap_list)))
                    keywords_data.append({"keyword": new_keyword, "keymap": new_keymap_list})
                    keyword_entry.delete(0, tk.END)
                    keymap_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", "Keymap must be a list.")
            except:
                messagebox.showerror("Error", "Invalid keymap format. Use list format.")

    tk.Button(add_frame, text="Add", command=add_new_entry).pack(side="left", padx=5)

    # Table for editing existing keywords
    tree = ttk.Treeview(editor_window, columns=("Keyword", "Keymap"), show="headings")
    tree.heading("Keyword", text="Keyword")
    tree.heading("Keymap", text="Keymap")
    tree.column("Keyword", width=200)
    tree.column("Keymap", width=350)
    tree.pack(pady=5, fill="both", expand=True)

    # Populate table
    for entry in keywords_data:
        tree.insert("", "end", values=(entry["keyword"], str(entry["keymap"])))

    def on_double_click(event):
        """Allows editing of the Keymap field."""
        selected_item = tree.selection()
        if not selected_item:
            return

        item = selected_item[0]
        keyword, current_keymap = tree.item(item, "values")

        # Prompt user to edit keymap
        new_keymap = simpledialog.askstring("Edit Keymap", f"Enter new keymap for '{keyword}':", initialvalue=current_keymap)
        if new_keymap is not None:
            try:
                new_keymap_list = eval(new_keymap)  # Convert string input to list
                if isinstance(new_keymap_list, list):
                    tree.item(item, values=(keyword, str(new_keymap_list)))
                    # Update the JSON data
                    for entry in keywords_data:
                        if entry["keyword"] == keyword:
                            entry["keymap"] = new_keymap_list
                            break
                else:
                    messagebox.showerror("Error", "Keymap must be a list.")
            except:
                messagebox.showerror("Error", "Invalid keymap format. Use list format.")

    tree.bind("<Double-Button-1>", on_double_click)  # Enable double-click editing

    def save_json():
        """Save the edited JSON back to the file."""
        new_data = {"mode": data.get("mode", ""), "keywords": keywords_data}
        with open(profile_path, "w") as f:
            json.dump(new_data, f, indent=4)
        messagebox.showinfo("Success", f"Changes saved to {profile_name}") # do I want
        editor_window.destroy() # close

    save_button = tk.Button(editor_window, text="Save Changes", command=save_json)
    save_button.pack(pady=5)

def edit_profiles():
    """Opens a simple profile management window."""
    edit_window = tk.Toplevel(tk_root)
    edit_window.title("Edit Profiles")
    edit_window.geometry("400x300")

    tk.Label(edit_window, text="Manage Profiles", font=("Arial", 14)).pack(pady=5)

    profiles_dir = "profiles"

    # Frame for the listbox and scrollbar
    listbox_frame = tk.Frame(edit_window)
    listbox_frame.pack(pady=5, fill="both", expand=True)

    profile_listbox = tk.Listbox(listbox_frame)
    profile_listbox.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=profile_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    profile_listbox.config(yscrollcommand=scrollbar.set)

    # Load profiles into the listbox
    profiles = [f for f in os.listdir(profiles_dir) if f.endswith(".json")]
    for profile in profiles:
        profile_listbox.insert(tk.END, profile)

    def open_json_editor(event):
        """Opens an editor to modify the JSON file."""
        selected_index = profile_listbox.curselection()
        if selected_index:
            profile_name = profile_listbox.get(selected_index[0])
            profile_path = os.path.join(profiles_dir, profile_name)

            try:
                with open(profile_path, "r") as f:
                    data = json.load(f)  # Load JSON data
            except json.JSONDecodeError:
                messagebox.showerror("Error", f"Invalid JSON in {profile_name}")
                return

            # Open the JSON editor
            open_json_table_editor(profile_name, profile_path, data)

    profile_listbox.bind("<Double-Button-1>", open_json_editor)  # Double-click event

    def add_profile():
        """Allows users to copy a default profile to create a new profile."""
        defaults_dir = os.path.join("profiles", "defaults")  # Folder containing default profiles
        profiles_dir = "profiles"  # Folder where user profiles are stored

        # Ensure the defaults directory exists
        if not os.path.exists(defaults_dir):
            os.makedirs(defaults_dir)

        # Get available default profiles
        default_profiles = [f for f in os.listdir(defaults_dir) if f.endswith(".json")]

        if not default_profiles:
            messagebox.showerror("Error", "No default profiles available. Please add defaults to the 'defaults' folder.")
            return

        # Ask the user to select a default profile
        selected_default = simpledialog.askstring("Select Default", f"Available Defaults:\n" + "\n".join(default_profiles) + "\n\nEnter the name of a default profile to copy:")

        if selected_default and selected_default in default_profiles:
            # Ask for a new profile name
            new_profile_name = simpledialog.askstring("New Profile", "Enter a name for the new profile:")
            if new_profile_name:
                new_profile_path = os.path.join(profiles_dir, f"{new_profile_name}.json")
                default_profile_path = os.path.join(defaults_dir, selected_default)

                # Copy default profile to new profile
                with open(default_profile_path, "r") as f:
                    default_data = json.load(f)

                with open(new_profile_path, "w") as f:
                    json.dump(default_data, f, indent=4)

                # Add to the listbox
                profile_listbox.insert(tk.END, f"{new_profile_name}.json")

                # Open the new profile in the JSON editor
                open_json_table_editor(f"{new_profile_name}.json", new_profile_path, default_data)
        else:
            messagebox.showwarning("Warning", "Invalid selection or action canceled.")

    def delete_profile():
        """Delete the selected profile."""
        selected_index = profile_listbox.curselection()
        if selected_index:
            profile_name = profile_listbox.get(selected_index[0])
            confirm = messagebox.askyesno("Delete Profile", f"Are you sure you want to delete '{profile_name}'?")
            if confirm:
                os.remove(os.path.join(profiles_dir, profile_name))
                profile_listbox.delete(selected_index)

    button_frame = tk.Frame(edit_window)
    button_frame.pack(pady=5, fill="x")

    tk.Button(button_frame, text="Add Profile", command=add_profile).pack(side="left", expand=True, padx=5)
    tk.Button(button_frame, text="Delete Profile", command=delete_profile).pack(side="right", expand=True, padx=5)



def start_handler(profile_name):
    """Starts the handler and writer processes with a shared queue."""
    global queue, handler_process, writer_process
    queue = multiprocessing.Queue()
    handler_process = multiprocessing.Process(target=process_queue, args=(queue, profile_name))
    handler_process.start()
    writer_process = multiprocessing.Process(target=write_to_queue, args=(queue,))
    writer_process.start()

def play_action():
    selected_profile = profile_var.get()
    if selected_profile == "Edit Profiles...":
        edit_profiles()  # Open the profile editor
    elif selected_profile:
        messagebox.showinfo("Play", f"Playing with profile: {selected_profile}")
        start_handler(selected_profile)  # Start game handler
    else:
        messagebox.showwarning("Warning", "Please select a profile.")
    

def about_action():
    about_window = tk.Toplevel(tk_root)
    about_window.title("About")
    about_window.geometry("300x150")
    tk.Label(about_window, text="This is a simple GUI app.", font=("Arial", 12)).pack(pady=20)

def stop():
    handler_process.kill()
    writer_process.kill()
    while not queue.empty():
        queue.get_nowait()

def refresh_profiles():
    """Refresh the profile dropdown options."""
    profile_menu["values"] = load_profiles()
    profile_var.set("")  # Reset selection
    # Rebind event to shift focus to Play button
    profile_menu.bind("<<ComboboxSelected>>", lambda event: play_button.focus())

if __name__ == "__main__":
    tk_root = tk.Tk()
    tk_root.title("EchoPlay")
    tk_root.geometry("800x400")

    profile_var = tk.StringVar()

    tk.Label(tk_root, text="Select Profile:", font=("Arial", 16)).pack(pady=5)
    profile_menu = ttk.Combobox(tk_root, textvariable=profile_var, state="readonly")
    profile_menu.pack(pady=5)

    refresh_profiles()  # Initialize profiles

    # Shift focus to the Play button when an option is selected
    profile_menu.bind("<<ComboboxSelected>>", lambda event: play_button.focus())

    play_button = tk.Button(tk_root, text="Play", command=play_action)
    play_button.pack(pady=5)

    about_button = tk.Button(tk_root, text="About", command=about_action)
    about_button.pack(pady=5)

    stop_button = tk.Button(tk_root, text="Stop", command=stop)
    stop_button.pack(pady=5)

    refresh_button = tk.Button(tk_root, text="Refresh Profiles", command=refresh_profiles)
    refresh_button.pack(pady=5)

    tk_root.mainloop()

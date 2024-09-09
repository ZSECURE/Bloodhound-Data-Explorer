import argparse
import json
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from PIL import Image, ImageTk

def load_bloodhound_data(users_file, groups_file, computers_file, domains_file):
    with open(users_file, 'r') as f:
        users_data = json.load(f)['data']
    with open(groups_file, 'r') as f:
        groups_data = json.load(f)['data']
    with open(computers_file, 'r') as f:
        computers_data = json.load(f)['data']
    with open(domains_file, 'r') as f:
        domains_data = json.load(f)['data']
    
    return users_data, groups_data, computers_data, domains_data

def build_tree_from_json(parent, data, tree, object_type):
    entries = []
    for entry in data:
        if isinstance(entry, dict):
            properties = entry.get('Properties', {})
            name = properties.get('name', 'Unknown')

            # Determine icon based on object type
            if object_type == 'computer':
                icon = tree.computer_icon
            elif object_type == 'group':
                icon = tree.group_icon
            elif object_type == 'domain':
                icon = tree.domain_icon
            else:
                icon = tree.user_icon

            # Store the entry as a JSON string in the tree view
            entries.append((name, json.dumps(entry), icon))
    
    # Sort entries alphabetically by name
    entries.sort(key=lambda x: x[0].lower())

    for name, entry_json, icon in entries:
        tree.insert(parent, 'end', text=name, open=True, image=icon, values=(entry_json,))

def on_tree_select(event, tree, detail_panel):
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        entry_json = item['values'][0]  # Retrieve the stored JSON string
        entry = json.loads(entry_json)  # Convert JSON string back to dictionary

        # Clear previous details
        detail_panel.delete('1.0', tk.END)

        # Display all attributes of the selected entry
        for key, value in entry.items():
            detail_panel.insert(tk.END, f"{key}: {value}\n")

def filter_tree(tree, search_var):
    search_term = search_var.get().lower()
    for item in tree.get_children():
        item_text = tree.item(item, 'text').lower()
        if search_term in item_text:
            tree.item(item, open=True)
            tree.see(item)
        else:
            tree.detach(item)
    
    # Reattach all items if search term is empty
    if not search_term:
        for item in tree.get_children():
            tree.reattach(item, '', 'end')

def create_gui_from_json(users_data, groups_data, computers_data, domains_data):
    root = tk.Tk()
    root.title("BloodHound Data Structure")
    root.geometry("1200x700")

    # Create a PanedWindow
    paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)

    # Create the notebook for the left pane
    left_notebook = ttk.Notebook(paned_window)
    left_notebook.pack(expand=True, fill='both')

    # Tabs for users, groups, computers, and domains
    user_tab = ttk.Frame(left_notebook)
    group_tab = ttk.Frame(left_notebook)
    computer_tab = ttk.Frame(left_notebook)
    domain_tab = ttk.Frame(left_notebook)

    left_notebook.add(user_tab, text='Users')
    left_notebook.add(group_tab, text='Groups')
    left_notebook.add(computer_tab, text='Computers')
    left_notebook.add(domain_tab, text='Domains')

    # Create treeviews for each tab
    user_tree = ttk.Treeview(user_tab, columns=("Entry",), show="tree")
    group_tree = ttk.Treeview(group_tab, columns=("Entry",), show="tree")
    computer_tree = ttk.Treeview(computer_tab, columns=("Entry",), show="tree")
    domain_tree = ttk.Treeview(domain_tab, columns=("Entry",), show="tree")

    user_tree.pack(expand=True, fill='both')
    group_tree.pack(expand=True, fill='both')
    computer_tree.pack(expand=True, fill='both')
    domain_tree.pack(expand=True, fill='both')

    # Load and assign icons to each specific tree
    user_tree.user_icon = ImageTk.PhotoImage(Image.open("user_icon.png").resize((16, 16)))
    group_tree.group_icon = ImageTk.PhotoImage(Image.open("group_icon.png").resize((16, 16)))
    computer_tree.computer_icon = ImageTk.PhotoImage(Image.open("computer_icon.png").resize((16, 16)))
    domain_tree.domain_icon = ImageTk.PhotoImage(Image.open("domain_icon.png").resize((16, 16)))

    # Build the trees from JSON data
    build_tree_from_json('', users_data, user_tree, 'user')
    build_tree_from_json('', groups_data, group_tree, 'group')
    build_tree_from_json('', computers_data, computer_tree, 'computer')
    build_tree_from_json('', domains_data, domain_tree, 'domain')

    # Create a search bar
    search_var = tk.StringVar()
    search_entry = ttk.Entry(root, textvariable=search_var)
    search_entry.pack(side=tk.TOP, fill=tk.X)
    search_var.trace("w", lambda name, index, mode: filter_tree(user_tree, search_var))

    # Create a detail panel on the right
    detail_frame = ttk.Frame(paned_window, padding=(10, 10))
    detail_panel = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD)
    detail_panel.pack(expand=True, fill='both')

    # Add frames to the paned window
    paned_window.add(left_notebook, weight=1)
    paned_window.add(detail_frame, weight=3)

    # Bind single-click events
    user_tree.bind('<<TreeviewSelect>>', lambda e: on_tree_select(e, user_tree, detail_panel))
    group_tree.bind('<<TreeviewSelect>>', lambda e: on_tree_select(e, group_tree, detail_panel))
    computer_tree.bind('<<TreeviewSelect>>', lambda e: on_tree_select(e, computer_tree, detail_panel))
    domain_tree.bind('<<TreeviewSelect>>', lambda e: on_tree_select(e, domain_tree, detail_panel))

    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="BloodHound JSON Viewer")
    parser.add_argument('--users', required=True, help='Path to BloodHound users JSON file')
    parser.add_argument('--groups', required=True, help='Path to BloodHound groups JSON file')
    parser.add_argument('--computers', required=True, help='Path to BloodHound computers JSON file')
    parser.add_argument('--domains', required=True, help='Path to BloodHound domains JSON file')
    
    args = parser.parse_args()

    users_data, groups_data, computers_data, domains_data = load_bloodhound_data(args.users, args.groups, args.computers, args.domains)
    create_gui_from_json(users_data, groups_data, computers_data, domains_data)

if __name__ == "__main__":
    main()

# welcome to TOS (Tryant of Sins)

# version 1.0.0

# author: Ervuln (Ishan Ghimire)

# A simple CLI tool to transfer media files from phone to PC via USB connection.

# Please read the LICENSE file before going to modify this tool

# Please read the README.md file for more information about this tool

import os
import subprocess
import platform
from datetime import datetime
from pathlib import Path

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    print("Installing required package: colorama")
    subprocess.run(["pip", "install", "colorama"], check=True)
    from colorama import init, Fore, Back, Style
    init(autoreset=True)


class Colors:
    """Professional gradient color scheme"""
    # Gradient colors - Blue to Cyan to Purple
    PRIMARY = Fore.CYAN
    SECONDARY = Fore.BLUE
    ACCENT = Fore.MAGENTA
    SUCCESS = Fore.GREEN
    ERROR = Fore.RED
    WARNING = Fore.YELLOW
    INFO = Fore.LIGHTCYAN_EX
    TEXT = Fore.WHITE
    DIM = Fore.LIGHTBLACK_EX
    HIGHLIGHT = Fore.LIGHTMAGENTA_EX


class UI:
    """Professional UI components"""
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def box_top(width=80):
        return f"{Colors.PRIMARY}╔{'═' * (width-2)}╗"
    
    @staticmethod
    def box_bottom(width=80):
        return f"{Colors.PRIMARY}╚{'═' * (width-2)}╝"
    
    @staticmethod
    def box_line(text, width=80, align='left'):
        padding = width - len(text) - 4
        if align == 'center':
            left_pad = padding // 2
            right_pad = padding - left_pad
            return f"{Colors.PRIMARY}║ {' ' * left_pad}{text}{' ' * right_pad} {Colors.PRIMARY}║"
        elif align == 'right':
            return f"{Colors.PRIMARY}║ {' ' * padding}{text} {Colors.PRIMARY}║"
        else:
            return f"{Colors.PRIMARY}║ {text}{' ' * padding} {Colors.PRIMARY}║"
    
    @staticmethod
    def separator(width=80, style='─'):
        return f"{Colors.DIM}{style * width}"
    
    @staticmethod
    def header(text):
        print(f"\n{Colors.ACCENT}@{Colors.HIGHLIGHT}{text} {Colors.ACCENT}@{Colors.TEXT}")
    
    @staticmethod
    def subheader(text):
        print(f"{Colors.INFO}┌─ {text}")
    
    @staticmethod
    def status_positive():
        return f"{Colors.SUCCESS}● CONNECTED"
    
    @staticmethod
    def status_negative():
        return f"{Colors.ERROR}● DISCONNECTED"
    
    @staticmethod
    def bullet(text, color=Colors.TEXT):
        return f"{Colors.PRIMARY}  ▸ {color}{text}"
    
    @staticmethod
    def progress_bar(current, total, width=40):
        filled = int(width * current / total)
        bar = '█' * filled + '░' * (width - filled)
        percentage = int(100 * current / total)
        return f"{Colors.PRIMARY}[{Colors.ACCENT}{bar}{Colors.PRIMARY}] {Colors.INFO}{percentage}%"


class AndroidTransfer:
    def __init__(self):
        self.device_connected = False
        self.device_name = "Unknown"
        self.pc_name = platform.node()
        self.current_path = ""
        
        # Here i am writing code for Media directories mapping
        self.media_dirs = {
            "1": {"name": "Images", "icon": "🖼️", "paths": ["/sdcard/DCIM", "/sdcard/Pictures"]},
            "2": {"name": "Audio", "icon": "🎵", "paths": ["/sdcard/Music", "/sdcard/Sounds", "/sdcard/Ringtones"]},
            "3": {"name": "Documents", "icon": "📄", "paths": [
                "/sdcard/Documents", 
                "/sdcard/Download",
                "/sdcard",  # this is thee root of storage
                "/storage/emulated/0/Documents",
                "/storage/emulated/0/Download"
            ]},
            "4": {"name": "Downloads", "icon": "📥", "paths": ["/sdcard/Download"]},
            "5": {"name": "Applications", "icon": "📱", "paths": ["/sdcard/Android/data"]},
            "6": {"name": "Videos", "icon": "🎬", "paths": ["/sdcard/DCIM", "/sdcard/Movies"]},
        }
    
    def print_banner(self):
        """Display professional gradient banner"""
        UI.clear_screen()
        banner = f"""
{Colors.PRIMARY}╔════════════════════════════════════════════════════════════════════════════╗
{Colors.PRIMARY}║                                                                            ║
{Colors.PRIMARY}║        {Colors.PRIMARY}         {Colors.SECONDARY}████████╗  {Colors.ACCENT} ██████╗   {Colors.HIGHLIGHT}  ███████╗{Colors.PRIMARY}       
{Colors.PRIMARY}║        {Colors.PRIMARY}         {Colors.SECONDARY}╚══██╔══╝  {Colors.ACCENT}██╔═══██╗  {Colors.HIGHLIGHT}  ██╔════╝{Colors.PRIMARY}
{Colors.PRIMARY}║        {Colors.PRIMARY}         {Colors.SECONDARY}   ██║     {Colors.ACCENT}██║   ██║  {Colors.HIGHLIGHT}  ███████╗{Colors.PRIMARY}
{Colors.PRIMARY}║        {Colors.PRIMARY}         {Colors.SECONDARY}   ██║     {Colors.ACCENT}██║   ██║  {Colors.HIGHLIGHT}  ╚════██║{Colors.PRIMARY}  
{Colors.PRIMARY}║        {Colors.PRIMARY}         {Colors.SECONDARY}   ██║     {Colors.ACCENT}╚██████╔╝  {Colors.HIGHLIGHT}  ███████║{Colors.PRIMARY}     
{Colors.PRIMARY}║        {Colors.PRIMARY}         {Colors.SECONDARY}   ╚═╝     {Colors.ACCENT} ╚═════╝   {Colors.HIGHLIGHT}  ╚══════╝{Colors.PRIMARY} 
{Colors.PRIMARY}║                                                                            
{Colors.PRIMARY}║                  {Colors.ACCENT}T R Y A N T   O F    S I N S  {Colors.PRIMARY}
{Colors.PRIMARY}║                                                                            
{Colors.PRIMARY}║   
{Colors.PRIMARY}║                                                                            
{Colors.PRIMARY}║  {Colors.INFO}Author        {Colors.DIM}│ {Colors.TEXT}Ishan Ghimire ( ervuln )                                            {Colors.PRIMARY}
{Colors.PRIMARY}║  {Colors.INFO}Version       {Colors.DIM}│ {Colors.TEXT}1.0.0                                                 {Colors.PRIMARY}
{Colors.PRIMARY}║  {Colors.INFO}Date          {Colors.DIM}│ {Colors.TEXT}{datetime.now().strftime('%B %d, %Y')}                                       {Colors.PRIMARY}
{Colors.PRIMARY}║  {Colors.INFO}Github        {Colors.DIM}│ {Colors.TEXT}https://github.com/ervuln   
{Colors.PRIMARY}║  {Colors.INFO}Linkedin      {Colors.DIM}│ {Colors.TEXT}https://www.linkedin.com/in/ishan-ghimire-2783b12a3   
{Colors.PRIMARY}║                                                                 
{Colors.PRIMARY}╚════════════════════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def check_adb(self):
        """Check if ADB is installed"""
        try:
            subprocess.run(["adb", "version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"\n{UI.box_top(76)}")
            print(UI.box_line(f"{Colors.ERROR}⚠ ERROR: ADB Not Found", 76, 'center'))
            print(UI.box_line("", 76))
            print(UI.box_line(f"{Colors.TEXT}Please install Android Debug Bridge (ADB)", 76, 'center'))
            print(UI.box_line(f"{Colors.INFO}https://developer.android.com/studio/releases/platform-tools", 76, 'center'))
            print(f"{UI.box_bottom(76)}\n")
            return False
    
    def check_device_connection(self):
        """Check if Android device is connected"""
        print(f"{Colors.INFO}⟳ Checking device connection...{Colors.TEXT}")
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')[1:]
            
            devices = [line.split('\t')[0] for line in lines if '\tdevice' in line]
            
            if devices:
                self.device_connected = True
                model = subprocess.run(["adb", "shell", "getprop", "ro.product.model"], 
                                     capture_output=True, text=True, check=True)
                self.device_name = model.stdout.strip()
                return True
            else:
                self.device_connected = False
                return False
        except subprocess.CalledProcessError:
            self.device_connected = False
            return False
    
    def display_status(self):
        """Display device connection status with gradient design"""
        print(f"\n{UI.box_top(76)}")
        print(UI.box_line(f"{Colors.ACCENT}CONNECTION STATUS", 76, 'center'))
        print(UI.box_line("", 76))
        
        status = UI.status_positive() if self.device_connected else UI.status_negative()
        
        print(UI.box_line(f"{Colors.INFO}Device Status    {Colors.DIM}│ {status}", 76))
        print(UI.box_line(f"{Colors.INFO}Phone Name       {Colors.DIM}│ {Colors.TEXT}{self.device_name}", 76))
        print(UI.box_line(f"{Colors.INFO}Computer Name    {Colors.DIM}│ {Colors.TEXT}{self.pc_name}", 76))
        print(f"{UI.box_bottom(76)}\n")
    
    def run_adb_command(self, command):
        """Execute ADB shell command"""
        try:
            result = subprocess.run(
                ["adb", "shell"] + command.split(),
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
    
    def list_directories(self, path):
        """List directories in given path"""
        try:
            result = subprocess.run(
                ["adb", "shell", "ls", "-d", f"{path}/*/"],
                capture_output=True,
                text=True
            )
            dirs = [d.strip().split('/')[-2] for d in result.stdout.strip().split('\n') if d.strip()]
            return dirs
        except:
            return []
    # i am fucking tired of writing codes lamo :(
    def list_files(self, path):
        """List files in given path"""
        try:
            result = subprocess.run(
                ["adb", "shell", "ls", "-p", path],
                capture_output=True,
                text=True
            )
            files = [f.strip() for f in result.stdout.strip().split('\n') 
                    if f.strip() and not f.endswith('/')]
            return files
        except:
            return []
    
    def list_files_recursive(self, path, extensions=None):
        """List files recursively with optional extension filter"""
        try:
            # Use find command to search recursively
            if extensions:
                # Build find command with extension filters
                ext_patterns = []
                for ext in extensions:
                    ext_patterns.append(f"-iname '*.{ext}'")
                ext_pattern = ' -o '.join(ext_patterns)
                
                result = subprocess.run(
                    ["adb", "shell", f"find {path} -type f \\( {ext_pattern} \\) 2>/dev/null"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
            else:
                result = subprocess.run(
                    ["adb", "shell", f"find {path} -type f 2>/dev/null"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
            
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                # Remove the base path and keep relative paths
                relative_files = []
                for f in files:
                    if f.startswith(path):
                        rel_path = f[len(path):].lstrip('/')
                        relative_files.append(rel_path)
                return relative_files
            return []
        except:
            return []
    
    def scan_all_documents(self):
        """Scan entire storage for document files"""
        print(f"{Colors.INFO}   Performing deep scan across all storage locations...")
        print(f"{Colors.DIM}   This may take a moment...\n")
        
        doc_extensions = ['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx', 
                         'odt', 'ods', 'odp', 'rtf', 'csv', 'zip', 'rar', '7z',
                         'epub', 'mobi', 'azw', 'azw3']
        
        all_files = []
        search_paths = [
            "/sdcard/Documents",
            "/sdcard/Download", 
            "/sdcard",
            "/storage/emulated/0/Documents",
            "/storage/emulated/0/Download"
        ]
        
        # Common app document folders locations
        app_folders = [
            "/sdcard/WhatsApp/Media/WhatsApp Documents",
            "/sdcard/Telegram/Telegram Documents",
            "/sdcard/Android/data/com.whatsapp/files",
            "/sdcard/Android/data/org.telegram.messenger/files"
        ]
        
        for path in search_paths + app_folders:
            try:
                files = self.list_files_recursive(path, doc_extensions)
                for f in files:
                    full_path = f"{path}/{f}"
                    # it helps to avoid duplicates
                    if full_path not in [item['full_path'] for item in all_files]:
                        all_files.append({
                            'display_name': f,
                            'full_path': full_path,
                            'base_path': path
                        })
            except:
                continue
        
        return all_files
    
    def get_installed_apps(self):
        """Get list of installed applications"""
        try:
            result = subprocess.run(
                ["adb", "shell", "pm", "list", "packages", "-3"],
                capture_output=True,
                text=True,
                check=True
            )
            packages = [line.replace("package:", "").strip() 
                       for line in result.stdout.strip().split('\n') if line.strip()]
            return sorted(packages)
        except:
            return []
    
    def get_apk_path(self, package_name):
        """Get APK file path for a package"""
        try:
            result = subprocess.run(
                ["adb", "shell", "pm", "path", package_name],
                capture_output=True,
                text=True,
                check=True
            )
            # this below code helps to Handle multiple APK paths (split APKs)
            paths = [line.replace("package:", "").strip() for line in result.stdout.strip().split('\n') if line.strip()]
            return paths if paths else None
        except:
            return None
    
    def display_main_menu(self):
        """Display main media selection menu"""
        UI.header("PHONE TO PC TRANSFER")
        print(f"{Colors.INFO}└─ Scanning available media directories...\n")
        
        print(f"{Colors.PRIMARY}┌{'─' * 74}┐")
        print(f"{Colors.PRIMARY}│ {Colors.INFO}{'Index':<12}{Colors.DIM}│ {Colors.INFO}{'Category':<57}{Colors.PRIMARY}│")
        print(f"{Colors.PRIMARY}├{'─' * 74}┤")
        
        for key, value in self.media_dirs.items():
            icon = value['icon']
            name = value['name']
            print(f"{Colors.PRIMARY}│ {Colors.ACCENT}{key:>4}        {Colors.DIM}│ {icon}  {Colors.TEXT}{name:<52}{Colors.PRIMARY}│")
        
        print(f"{Colors.PRIMARY}└{'─' * 74}┘\n")
    
    def display_subdirectories(self, media_type):
        """Display subdirectories for selected media type"""
        media_info = self.media_dirs[media_type]
        icon = media_info['icon']
        
        UI.header(f"{icon}  {media_info['name'].upper()}")
        print(f"{Colors.INFO}└─ Scanning folders...\n")
        
        all_dirs = []
        for base_path in media_info['paths']:
            dirs = self.list_directories(base_path)
            all_dirs.extend([(d, base_path) for d in dirs])
        
        if not all_dirs:
            all_dirs = [(p.split('/')[-1], p) for p in media_info['paths']]
        
        print(f"{Colors.PRIMARY}┌{'─' * 74}┐")
        print(f"{Colors.PRIMARY}│ {Colors.INFO}{'Index':<12}{Colors.DIM}│ {Colors.INFO}{'Folder Name':<57}{Colors.PRIMARY}│")
        print(f"{Colors.PRIMARY}├{'─' * 74}┤")
        print(f"{Colors.PRIMARY}│ {Colors.ACCENT}{1:>4}        {Colors.DIM}│ {Colors.SUCCESS}📁 All Folders{' ' * 42}{Colors.PRIMARY}│")
        
        for idx, (dir_name, _) in enumerate(all_dirs, 2):
            display_name = (dir_name[:52] + '...') if len(dir_name) > 52 else dir_name
            print(f"{Colors.PRIMARY}│ {Colors.ACCENT}{idx:>4}        {Colors.DIM}│ {Colors.TEXT}📁 {display_name:<52}{Colors.PRIMARY}│")
        
        print(f"{Colors.PRIMARY}└{'─' * 74}┘\n")
        
        return all_dirs
    
    def display_files(self, path, media_type=None):
        """Display files in the selected directory"""
        
        # For documents, it will perform comprehensive scan
        if media_type == "3":  # Documents
            UI.subheader(f"Scanning: {Colors.HIGHLIGHT}All Storage Locations")
            all_docs = self.scan_all_documents()
            
            if not all_docs:
                print(f"{Colors.ERROR}   ✗ No document files found!\n")
                return []
            
            print(f"{Colors.PRIMARY}┌{'─' * 74}┐")
            print(f"{Colors.PRIMARY}│ {Colors.INFO}{'Index':<12}{Colors.DIM}│ {Colors.INFO}{'File Name & Location':<57}{Colors.PRIMARY}│")
            print(f"{Colors.PRIMARY}├{'─' * 74}┤")
            
            for idx, doc in enumerate(all_docs, 1):
                display_name = (doc['display_name'][:52] + '...') if len(doc['display_name']) > 52 else doc['display_name']
                print(f"{Colors.PRIMARY}│ {Colors.ACCENT}{idx:>4}        {Colors.DIM}│ {Colors.TEXT}{display_name:<55}{Colors.PRIMARY}│")
            
            print(f"{Colors.PRIMARY}└{'─' * 74}┘")
            print(f"{Colors.DIM}   Total: {len(all_docs)} documents found across all locations\n")
            
            return all_docs
        
        # For other media types, it will use standard or recursive search
        else:
            UI.subheader(f"Directory: {Colors.HIGHLIGHT}{path}")
            print(f"{Colors.INFO}   Loading files...\n")
            
            files = self.list_files(path)
            
            if not files:
                print(f"{Colors.ERROR}   ✗ No files found in this directory!\n")
                return []
            
            print(f"{Colors.PRIMARY}┌{'─' * 74}┐")
            print(f"{Colors.PRIMARY}│ {Colors.INFO}{'Index':<12}{Colors.DIM}│ {Colors.INFO}{'File Name':<57}{Colors.PRIMARY}│")
            print(f"{Colors.PRIMARY}├{'─' * 74}┤")
            
            for idx, file in enumerate(files, 1):
                display_name = (file[:52] + '...') if len(file) > 52 else file
                print(f"{Colors.PRIMARY}│ {Colors.ACCENT}{idx:>4}        {Colors.DIM}│ {Colors.TEXT}{display_name:<55}{Colors.PRIMARY}│")
            
            print(f"{Colors.PRIMARY}└{'─' * 74}┘")
            print(f"{Colors.DIM}   Total: {len(files)} files\n")
            
            return files
    
    def display_apps(self):
        """Display installed applications"""
        UI.header("📱 INSTALLED APPLICATIONS")
        print(f"{Colors.INFO}└─ Scanning third-party apps...\n")
        
        apps = self.get_installed_apps()
        
        if not apps:
            print(f"{Colors.ERROR}   ✗ No third-party apps found!\n")
            return []
        
        print(f"{Colors.PRIMARY}┌{'─' * 74}┐")
        print(f"{Colors.PRIMARY}│ {Colors.INFO}{'Index':<12}{Colors.DIM}│ {Colors.INFO}{'Package Name':<57}{Colors.PRIMARY}│")
        print(f"{Colors.PRIMARY}├{'─' * 74}┤")
        
        for idx, app in enumerate(apps, 1):
            display_name = (app[:52] + '...') if len(app) > 52 else app
            print(f"{Colors.PRIMARY}│ {Colors.ACCENT}{idx:>4}        {Colors.DIM}│ {Colors.TEXT}{display_name:<55}{Colors.PRIMARY}│")
        
        print(f"{Colors.PRIMARY}└{'─' * 74}┘")
        print(f"{Colors.DIM}   Total: {len(apps)} applications\n")
        
        return apps
    
    def parse_selection(self, selection, max_items):
        """Parse user selection (all, single, range, multiple)"""
        selection = selection.strip().lower()
        
        if selection == "all":
            return list(range(1, max_items + 1))
        
        indices = []
        parts = selection.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                indices.extend(range(start, end + 1))
            else:
                indices.append(int(part))
        
        return [i for i in indices if 1 <= i <= max_items]
    
    def open_folder(self, path):
        """Open folder in file explorer"""
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except:
            pass
    
    def transfer_files(self, files, source_path, dest_folder, media_type=None):
        """Transfer files from phone to PC"""
        dest_path = Path.home() / "AndroidTransfer" / dest_folder
        dest_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{UI.box_top(76)}")
        print(UI.box_line(f"{Colors.ACCENT}TRANSFER DESTINATION", 76, 'center'))
        print(UI.box_line(f"{Colors.TEXT}{str(dest_path)}", 76, 'center'))
        print(f"{UI.box_bottom(76)}\n")
        
        success_count = 0
        failed_count = 0
        
        print(f"{Colors.INFO}⟳ Starting transfer...\n")
        
        for idx, file in enumerate(files, 1):
            # the below code handle document objects with full paths
            if media_type == "3" and isinstance(file, dict):
                source = file['full_path']
                file_name = Path(file['display_name']).name
                dest = dest_path / file_name
                display_name = file['display_name']
            # the below code handle full paths for recursive search
            elif '/' in str(file):
                source = f"{source_path}/{file}"
                # the below code will create subdirectories if needed
                file_dest_path = dest_path / Path(file).parent
                file_dest_path.mkdir(parents=True, exist_ok=True)
                dest = dest_path / file
                display_name = file
            else:
                source = f"{source_path}/{file}"
                dest = dest_path / file
                display_name = file
            
            display_name = (str(display_name)[:45] + '...') if len(str(display_name)) > 45 else str(display_name)
            print(f"{Colors.PRIMARY}[{Colors.ACCENT}{idx:>3}{Colors.PRIMARY}/{Colors.ACCENT}{len(files):<3}{Colors.PRIMARY}] {Colors.TEXT}{display_name:<50}", end=" ")
            
            try:
                subprocess.run(["adb", "pull", source, str(dest)], 
                             capture_output=True, check=True)
                print(f"{Colors.SUCCESS}✓")
                success_count += 1
            except subprocess.CalledProcessError:
                print(f"{Colors.ERROR}✗")
                failed_count += 1
        
        # these are the summary of transfer
        print(f"\n{UI.box_top(76)}")
        print(UI.box_line(f"{Colors.ACCENT}TRANSFER COMPLETE", 76, 'center'))
        print(UI.box_line("", 76))
        print(UI.box_line(f"{Colors.SUCCESS}● Success    {Colors.DIM}│ {Colors.TEXT}{success_count} files", 76))
        print(UI.box_line(f"{Colors.ERROR}● Failed     {Colors.DIM}│ {Colors.TEXT}{failed_count} files", 76))
        print(UI.box_line(f"{Colors.INFO}● Total      {Colors.DIM}│ {Colors.TEXT}{len(files)} files", 76))
        print(f"{UI.box_bottom(76)}\n")
        
        open_choice = input(f"{Colors.PRIMARY}► {Colors.INFO}Open folder? {Colors.DIM}(y/n): {Colors.TEXT}").strip().lower()
        if open_choice == 'y':
            self.open_folder(str(dest_path))
            print(f"{Colors.SUCCESS}✓ Opening folder...\n")
    
    def transfer_apps(self, apps, app_packages):
        """Transfer APK files from phone to PC"""
        dest_path = Path.home() / "AndroidTransfer" / "Applications"
        dest_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{UI.box_top(76)}")
        print(UI.box_line(f"{Colors.ACCENT}APK EXTRACTION", 76, 'center'))
        print(UI.box_line(f"{Colors.TEXT}{str(dest_path)}", 76, 'center'))
        print(f"{UI.box_bottom(76)}\n")
        
        success_count = 0
        failed_count = 0
        
        print(f"{Colors.INFO}⟳ Extracting APK files...\n")
        
        for idx, package in enumerate(apps, 1):
            apk_paths = self.get_apk_path(package)
            
            display_name = (package[:45] + '...') if len(package) > 45 else package
            
            if not apk_paths:
                print(f"{Colors.PRIMARY}[{Colors.ACCENT}{idx:>3}{Colors.PRIMARY}/{Colors.ACCENT}{len(apps):<3}{Colors.PRIMARY}] {Colors.TEXT}{display_name:<50} {Colors.ERROR}✗ (Path not found)")
                failed_count += 1
                continue
            
            print(f"{Colors.PRIMARY}[{Colors.ACCENT}{idx:>3}{Colors.PRIMARY}/{Colors.ACCENT}{len(apps):<3}{Colors.PRIMARY}] {Colors.TEXT}{display_name:<50}", end=" ")
            
            # it helps to handle split APKs (multiple files)
            if len(apk_paths) > 1:
                # it will create a directory for split APKs
                safe_name = package.replace(".", "_")
                app_dir = dest_path / safe_name
                app_dir.mkdir(exist_ok=True)
                
                all_success = True
                for i, apk_path in enumerate(apk_paths):
                    try:
                        dest_file = app_dir / f"base_{i}.apk"
                        result = subprocess.run(
                            ["adb", "pull", apk_path, str(dest_file)], 
                            capture_output=True, 
                            check=True, 
                            timeout=60
                        )
                        if b"error" in result.stderr.lower() or b"failed" in result.stderr.lower():
                            all_success = False
                            break
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        all_success = False
                        break
                
                if all_success:
                    print(f"{Colors.SUCCESS}✓ (Split APK)")
                    success_count += 1
                else:
                    print(f"{Colors.ERROR}✗ (Transfer failed)")
                    failed_count += 1
            else:
                # Single APK file
                safe_name = package.replace(".", "_") + ".apk"
                dest = dest_path / safe_name
                
                try:
                    result = subprocess.run(
                        ["adb", "pull", apk_paths[0], str(dest)], 
                        capture_output=True, 
                        check=True, 
                        timeout=60
                    )
                    # it will check if pull was actually successful
                    if dest.exists() and dest.stat().st_size > 0:
                        print(f"{Colors.SUCCESS}✓")
                        success_count += 1
                    else:
                        print(f"{Colors.ERROR}✗ (Empty file)")
                        failed_count += 1
                        if dest.exists():
                            dest.unlink()  # it will remove empty file
                except subprocess.TimeoutExpired:
                    print(f"{Colors.ERROR}✗ (Timeout)")
                    failed_count += 1
                except subprocess.CalledProcessError as e:
                    # it will check stderr for permission issues
                    stderr = e.stderr.decode() if e.stderr else ""
                    if "permission denied lol " in stderr.lower():
                        print(f"{Colors.ERROR}✗ (Permission denied lol)")
                    elif "not found" in stderr.lower():
                        print(f"{Colors.ERROR}✗ (File not found)")
                    else:
                        print(f"{Colors.ERROR}✗ (Transfer failed)")
                    failed_count += 1
        
        # summary of extraction MF
        print(f"\n{UI.box_top(76)}")
        print(UI.box_line(f"{Colors.ACCENT}EXTRACTION COMPLETE", 76, 'center'))
        print(UI.box_line("", 76))
        print(UI.box_line(f"{Colors.SUCCESS}● Success    {Colors.DIM}│ {Colors.TEXT}{success_count} apps", 76))
        print(UI.box_line(f"{Colors.ERROR}● Failed     {Colors.DIM}│ {Colors.TEXT}{failed_count} apps", 76))
        print(UI.box_line(f"{Colors.INFO}● Total      {Colors.DIM}│ {Colors.TEXT}{len(apps)} apps", 76))
        
        if failed_count > 0:
            print(UI.box_line("", 76))
            print(UI.box_line(f"{Colors.WARNING}Note: Some apps may be protected or use split APKs", 76, 'center'))
        
        print(f"{UI.box_bottom(76)}\n")
        
        if success_count > 0:
            open_choice = input(f"{Colors.PRIMARY}► {Colors.INFO}Open folder? {Colors.DIM}(y/n): {Colors.TEXT}").strip().lower()
            if open_choice == 'y':
                self.open_folder(str(dest_path))
                print(f"{Colors.SUCCESS}✓ Opening folder...\n")
    
    def run(self):
        """Main application loop"""
        self.print_banner()
        
        if not self.check_adb():
            return
        
        if not self.check_device_connection():
            self.display_status()
            print(f"{UI.box_top(76)}")
            print(UI.box_line(f"{Colors.ERROR}⚠ CONNECTION ERROR", 76, 'center'))
            print(UI.box_line("", 76))
            print(UI.box_line(f"{Colors.TEXT}No device connected via USB", 76, 'center'))
            print(UI.box_line(f"{Colors.INFO}My guy please enable USB debugging on your device", 76, 'center'))
            print(f"{UI.box_bottom(76)}\n")
            return
        
        self.display_status()
        
        while True:
            self.display_main_menu()
            
            try:
                choice = input(f"{Colors.PRIMARY}► {Colors.INFO}Select category {Colors.DIM}(1-6 or 'q' to quit): {Colors.TEXT}").strip()
                
                if choice.lower() == 'q':
                    print(f"\n{Colors.ACCENT}$ {Colors.SUCCESS}Thank you for using Tryant of sins  ( TOS )! {Colors.ACCENT}${Colors.TEXT}\n")
                    break
                
                if choice not in self.media_dirs:
                    print(f"{Colors.ERROR}✗ Invalid choice! Please select 1-6\n")
                    input(f"{Colors.DIM}Press Enter to continue...")
                    continue
                
                # the below code is for special handling for Applications
                if choice == "5":
                    apps = self.display_apps()
                    
                    if not apps:
                        input(f"{Colors.DIM}Press Enter to continue...")
                        continue
                    
                    app_choice = input(f"{Colors.PRIMARY}► {Colors.INFO}Select apps {Colors.DIM}(all, 1,2,3 or 1-5): {Colors.TEXT}").strip()
                    
                    selected_indices = self.parse_selection(app_choice, len(apps))
                    selected_apps = [apps[i-1] for i in selected_indices]
                    
                    if selected_apps:
                        self.transfer_apps(selected_apps, apps)
                    
                    continue_choice = input(f"{Colors.PRIMARY}► {Colors.INFO}Transfer more mf ? {Colors.DIM}(y/n): {Colors.TEXT}").strip().lower()
                    if continue_choice != 'y':
                        print(f"\n{Colors.ACCENT}${Colors.SUCCESS}Dude thank you for using Tryant of sins  ( TOS )!{Colors.ACCENT}${Colors.TEXT}\n")
                        break
                    continue
                
                # the below code is for special handling for Documents - skip folder selection
                if choice == "3":
                    files = self.display_files(None, choice)
                    
                    if not files:
                        input(f"{Colors.DIM}Yo bro press Enter to continue...")
                        continue
                    
                    file_choice = input(f"{Colors.PRIMARY}► {Colors.INFO}Select files {Colors.DIM}(all, 1,2,3 or 1-5): {Colors.TEXT}").strip()
                    
                    selected_indices = self.parse_selection(file_choice, len(files))
                    selected_files = [files[i-1] for i in selected_indices]
                    
                    if selected_files:
                        self.transfer_files(selected_files, None, 
                                          self.media_dirs[choice]['name'], choice)
                    
                    continue_choice = input(f"{Colors.PRIMARY}► {Colors.INFO}Transfer more mf ? {Colors.DIM}(y/n): {Colors.TEXT}").strip().lower()
                    if continue_choice != 'y':
                        print(f"\n{Colors.ACCENT}$ {Colors.SUCCESS}Thank you for using Tryant of sins  ( TOS )!{Colors.ACCENT}${Colors.TEXT}\n")
                        break
                    continue
                
                # the below code will show subdirectories for other media types
                dirs = self.display_subdirectories(choice)
                
                if not dirs:
                    print(f"{Colors.ERROR}✗ No directories found!\n")
                    input(f"{Colors.DIM}My guy press Enter to continue...")
                    continue
                
                dir_choice = input(f"{Colors.PRIMARY}► {Colors.INFO}Select folder {Colors.DIM}(1 for All, 2-{len(dirs)+1}): {Colors.TEXT}").strip()
                
                if dir_choice == "1":
                    selected_path = self.media_dirs[choice]['paths'][0]
                else:
                    idx = int(dir_choice) - 2
                    if 0 <= idx < len(dirs):
                        selected_path = f"{dirs[idx][1]}/{dirs[idx][0]}"
                    else:
                        print(f"{Colors.ERROR}✗ Invalid selection!\n")
                        input(f"{Colors.DIM}Dude press Enter to continue...")
                        continue
                
                #  this fucking below code will show files
                files = self.display_files(selected_path, choice)
                
                if not files:
                    input(f"{Colors.DIM}Bro press Enter to continue...")
                    continue
                
                file_choice = input(f"{Colors.PRIMARY}► {Colors.INFO}Select files {Colors.DIM}(all, 1,2,3 or 1-5): {Colors.TEXT}").strip()
                
                selected_indices = self.parse_selection(file_choice, len(files))
                selected_files = [files[i-1] for i in selected_indices]
                
                if selected_files:
                    self.transfer_files(selected_files, selected_path, 
                                      self.media_dirs[choice]['name'], choice)
                
                continue_choice = input(f"{Colors.PRIMARY}► {Colors.INFO}Transfer more? {Colors.DIM}(y/n): {Colors.TEXT}").strip().lower()
                if continue_choice != 'y':
                    print(f"\n{Colors.ACCENT} $ {Colors.SUCCESS}Man thank you for using Tryant of sins  ( TOS )! {Colors.ACCENT}${Colors.TEXT}\n")
                    break
                    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.WARNING}⚠ Transfer cancelled by user.\n")
                break
            except Exception as e:
                print(f"\n{Colors.ERROR}✗ ERROR: {str(e)}\n")
                input(f"{Colors.DIM}Bruh press Enter to continue...")
                continue


def main():
    from TOS.android_transfer import AndroidTransfer
    app = AndroidTransfer()
    app.run()

if __name__ == "__main__":
    main()

# Finally end of the code 

# This tool is developed by Ishan Ghimire ( ervuln )

# If you find any issues or have suggestions, please report them on GitHub

# If you don't like this tool , then go and fuck yourself mf 

# If you like this tool , then don't forget to give the star - cause it helps me to get motivate dude :)

# # Thank you for using Tryant of sins  ( TOS )!  

# Have a pretty good day and enjoy your coffee!!!


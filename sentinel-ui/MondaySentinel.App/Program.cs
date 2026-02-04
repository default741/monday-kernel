using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Net.Http;
using System.Net.Http.Json;

class Program
{
    // --- Windows API Imports ---
    [DllImport("user32.dll")]
    static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [DllImport("user32.dll")]
    private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

    [DllImport("user32.dll")]
    private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

    // Hotkey Constants
    const uint ALT = 0x0001;
    const uint SPACE = 0x20;
    const int HOTKEY_ID = 9000;

    private static SearchOverlay? _overlay;

    static void Main(string[] args)
    {
        Console.WriteLine("🚀 Monday Sentinel: System-Wide Intelligence Active.");

        // 1. Run the Window Observer in a background thread
        Task.Run(() => StartWindowObserver());

        // 2. Setup the UI Overlay
        _overlay = new SearchOverlay();

        // 3. Setup a hidden form to listen for the Global Hotkey
        Application.Run(new HotkeyWindow());
    }

    static async Task StartWindowObserver()
    {
        string lastWindow = "";
        using var client = new HttpClient();

        while (true)
        {
            IntPtr handle = GetForegroundWindow();
            StringBuilder sysText = new StringBuilder(256);
            if (GetWindowText(handle, sysText, 256) > 0)
            {
                string currentWindow = sysText.ToString();
                if (currentWindow != lastWindow)
                {
                    lastWindow = currentWindow;
                    Console.WriteLine($"🔍 Focus: {currentWindow}");
                    try {
                        var payload = new { window = currentWindow };
                        await client.PostAsJsonAsync("http://localhost:3000/state/update", payload);
                    } catch { /* Silent fail if orchestrator is down */ }
                }
            }
            await Task.Delay(2000);
        }
    }

    // A hidden window that processes the Hotkey "Alt + Space"
    class HotkeyWindow : Form
    {
        public HotkeyWindow()
        {
            this.Visible = false;
            this.WindowState = FormWindowState.Minimized;
            this.ShowInTaskbar = false;

            // Register Alt + Space
            RegisterHotKey(this.Handle, HOTKEY_ID, ALT, SPACE);
        }

        protected override void WndProc(ref Message m)
        {
            if (m.Msg == 0x0312 && m.WParam.ToInt32() == HOTKEY_ID)
            {
                Console.WriteLine("🧠 Cerebro HUD Triggered!");
                _overlay?.Show();
                _overlay?.Activate();
            }
            base.WndProc(ref m);
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            UnregisterHotKey(this.Handle, HOTKEY_ID);
            base.OnFormClosing(e);
        }
    }
}
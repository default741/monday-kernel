using System;
using System.Windows.Forms;
using System.Drawing;
using System.Net.Http;
using System.Runtime.InteropServices;
using System.Text.Json; // Fixes the JsonSerializer error
using System.Collections.Generic; // For List support

// Models stay at the top or in a namespace
public class KernelResponse
{
    public string status { get; set; } = "";
    public SearchResults results { get; set; } = new();
}

public class SearchResults
{
    public List<string> semantic_matches { get; set; } = new();
    public List<GraphMatch> structural_matches { get; set; } = new();
}

public class GraphMatch
{
    public string content { get; set; } = "";
    public string tag { get; set; } = "";
}

public class SearchOverlay : Form
{
    private TextBox searchInput;
    private ListBox resultsList;

    // Fixes the 'client' error: Create a static client for this class
    private static readonly HttpClient client = new HttpClient();

    public SearchOverlay()
    {
        this.FormBorderStyle = FormBorderStyle.None;
        this.StartPosition = FormStartPosition.CenterScreen;
        this.Size = new Size(600, 400);
        this.BackColor = Color.FromArgb(20, 20, 20);
        this.Opacity = 0.95;
        this.TopMost = true;

        searchInput = new TextBox {
            Dock = DockStyle.Top,
            Font = new Font("Segoe UI", 18),
            BackColor = Color.FromArgb(45, 45, 45),
            ForeColor = Color.White,
            BorderStyle = BorderStyle.FixedSingle
        };

        resultsList = new ListBox {
            Dock = DockStyle.Fill,
            BackColor = Color.FromArgb(20, 20, 20),
            ForeColor = Color.LightGray,
            Font = new Font("Segoe UI", 12),
            BorderStyle = BorderStyle.None
        };

        this.Controls.Add(resultsList);
        this.Controls.Add(searchInput);

        searchInput.KeyDown += async (s, e) => {
            if (e.KeyCode == Keys.Enter) await PerformSearch();
            if (e.KeyCode == Keys.Escape) this.Hide();
        };
    }

    private async Task PerformSearch()
    {
        string query = searchInput.Text;
        if (string.IsNullOrWhiteSpace(query)) return;

        resultsList.Items.Clear();
        resultsList.Items.Add("🧠 Recalling memories...");

        if (query.StartsWith("/listen"))
        {
            resultsList.Items.Clear();
            resultsList.Items.Add("📡 Sending toggle command...");
            try {
                await client.PostAsync("http://localhost:3000/command/listen", null);
                resultsList.Items.Add("✅ Secretary state toggled!");
                searchInput.Text = ""; // Clear for next use
            } catch {
                resultsList.Items.Add("❌ Failed to reach Orchestrator.");
            }
            return;
        }

        try
        {
            // 1. Fetch data from Rust Orchestrator
            var responseStream = await client.GetStreamAsync($"http://localhost:3000/query?q={query}");

            // 2. Parse the JSON
            var data = await JsonSerializer.DeserializeAsync<KernelResponse>(responseStream);

            resultsList.Items.Clear();

            if (data?.results != null)
            {
                if (data.results.semantic_matches.Count > 0)
                {
                    resultsList.Items.Add("--- SEMANTIC MATCHES ---");
                    foreach (var match in data.results.semantic_matches)
                    {
                        resultsList.Items.Add($"✨ {match}");
                    }
                }

                if (data.results.structural_matches.Count > 0)
                {
                    resultsList.Items.Add("");
                    resultsList.Items.Add("--- GRAPH CONNECTIONS ---");
                    foreach (var match in data.results.structural_matches)
                    {
                        resultsList.Items.Add($"🏷️ [{match.tag}] {match.content}");
                    }
                }
            }

            if (resultsList.Items.Count == 0 || (data?.results.semantic_matches.Count == 0 && data?.results.structural_matches.Count == 0))
                resultsList.Items.Add("No memories found for that query.");

        }
        catch (Exception ex)
        {
            resultsList.Items.Clear();
            resultsList.Items.Add($"❌ Error: {ex.Message}");
        }
    }

    [DllImport("Gdi32.dll", EntryPoint = "CreateRoundRectRgn")]
    private static extern IntPtr CreateRoundRectRgn(int nLeftRect, int nTopRect, int nRightRect, int nBottomRect, int nWidthEllipse, int nHeightEllipse);

    protected override void OnLoad(EventArgs e)
    {
        base.OnLoad(e);
        this.Region = Region.FromHrgn(CreateRoundRectRgn(0, 0, Width, Height, 20, 20));
    }
}
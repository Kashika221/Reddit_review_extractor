import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Search, BarChart3, TrendingUp, MessageSquare, Newspaper } from "lucide-react";

const Dashboard = () => {
  const [companyName, setCompanyName] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();
    setIsAnalyzing(true);
    // Analysis logic will be added later
    console.log("Analyzing company:", companyName);
    // Simulate analysis
    setTimeout(() => setIsAnalyzing(false), 2000);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
      <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-accent" />
            <span className="text-xl font-semibold">CompanyPulse</span>
          </div>
          <Button variant="outline">Logout</Button>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8">
        {/* Search Section */}
        <div className="max-w-3xl mx-auto mb-12">
          <Card className="shadow-card border-border">
            <CardHeader>
              <CardTitle>Analyze Company Sentiment</CardTitle>
              <CardDescription>
                Enter a company name to analyze their public perception across social media and news
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAnalyze} className="flex gap-4">
                <Input
                  placeholder="Enter company name..."
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  required
                  className="flex-1"
                />
                <Button 
                  type="submit" 
                  disabled={isAnalyzing}
                  className="bg-accent text-accent-foreground hover:bg-accent/90"
                >
                  <Search className="mr-2 h-4 w-4" />
                  {isAnalyzing ? "Analyzing..." : "Analyze"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Results Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="shadow-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Twitter Sentiment</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-accent">--</div>
              <p className="text-xs text-muted-foreground mt-1">
                Awaiting analysis
              </p>
            </CardContent>
          </Card>

          <Card className="shadow-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Reddit Sentiment</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-accent">--</div>
              <p className="text-xs text-muted-foreground mt-1">
                Awaiting analysis
              </p>
            </CardContent>
          </Card>

          <Card className="shadow-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">News Sentiment</CardTitle>
              <Newspaper className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-accent">--</div>
              <p className="text-xs text-muted-foreground mt-1">
                Awaiting analysis
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Visualization Section */}
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="shadow-card border-border">
            <CardHeader>
              <CardTitle>Sentiment Over Time</CardTitle>
              <CardDescription>Trend analysis across all sources</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-muted/30 rounded-lg">
                <p className="text-muted-foreground">Chart will appear here</p>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-card border-border">
            <CardHeader>
              <CardTitle>Source Distribution</CardTitle>
              <CardDescription>Breakdown by platform</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-muted/30 rounded-lg">
                <p className="text-muted-foreground">Chart will appear here</p>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-card border-border md:col-span-2">
            <CardHeader>
              <CardTitle>Overall Company Image</CardTitle>
              <CardDescription>AI-generated summary of public perception</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-6 bg-muted/30 rounded-lg">
                <p className="text-muted-foreground text-center">
                  Enter a company name and click "Analyze" to see results
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

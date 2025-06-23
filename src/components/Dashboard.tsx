import { useState, useEffect } from "react";
import { ArrowLeft, Sparkles, TrendingUp, Clock, Target, Share2, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import MetabolicChart from "@/components/MetabolicChart";
import { insightsService, type Insight } from "@/services/insightsService";
import { authService } from "@/services/authService";
import { useToast } from "@/hooks/use-toast";

interface DashboardProps {
  onBack: () => void;
}

const Dashboard = ({ onBack }: DashboardProps) => {
  const [selectedInsight, setSelectedInsight] = useState(0);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      const currentUser = authService.getCurrentUser();
      if (!currentUser?.id) {
        throw new Error("User not authenticated");
      }

      const response = await insightsService.getUserInsights(currentUser.id);
      setInsights(response.insights);
      
      if (response.insights.length === 0) {
        toast({
          title: "No insights available",
          description: "Upload more data to generate personalized insights.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Failed to load insights:', error);
      toast({
        title: "Failed to load insights",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
      
      // Fallback to sample data for demo purposes
      setInsights([
        {
          id: '1',
          title: "Carb Timing Sweet Spot",
          pattern: "60% better glucose response to carbs before 2pm vs after 6pm",
          confidence: 87,
          description: "Your body processes carbohydrates significantly more efficiently in the earlier part of the day. This pattern was consistent across 12 of your 14 tracked days.",
          actionable: "Consider having your largest carb portions at breakfast and lunch, with lighter, protein-focused dinners.",
          data_points: 156,
          correlation: 0.72,
          created_at: new Date().toISOString(),
        },
        // ... other sample insights
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleShareInsights = async () => {
    try {
      const shareData = {
        title: 'My Gluco-Lens Insights',
        text: `Check out my personalized metabolic insights from Gluco-Lens!`,
        url: window.location.href,
      };

      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        await navigator.clipboard.writeText(window.location.href);
        toast({
          title: "Link copied!",
          description: "Share link has been copied to your clipboard.",
        });
      }
    } catch (error) {
      console.error('Failed to share:', error);
    }
  };

  const handleDownloadReport = async () => {
    try {
      // This would typically generate a PDF or detailed report
      const reportData = {
        insights: insights,
        generated_at: new Date().toISOString(),
        user: authService.getCurrentUser(),
      };

      const blob = new Blob([JSON.stringify(reportData, null, 2)], {
        type: 'application/json',
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `gluco-lens-insights-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast({
        title: "Report downloaded!",
        description: "Your insights report has been saved to your device.",
      });
    } catch (error) {
      console.error('Failed to download report:', error);
      toast({
        title: "Download failed",
        description: "Failed to generate report. Please try again.",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <Card className="w-full max-w-md shadow-2xl bg-white/95 backdrop-blur-sm border-0">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading your insights...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentInsight = insights[selectedInsight];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4">
      <div className="container mx-auto max-w-6xl">
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={onBack} 
            className="mb-6 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>

          <div className="text-center mb-8">
            <Badge variant="outline" className="mb-4 px-4 py-2 bg-white/80 backdrop-blur-sm">
              <Sparkles className="w-4 h-4 mr-2" />
              Analysis Complete
            </Badge>
            <h1 className="text-4xl font-bold mb-4">Your Unique Metabolic Story</h1>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              We analyzed 14 days of your data and discovered some surprising patterns. 
              Here are your most significant insights.
            </p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Insights List */}
          <div className="lg:col-span-1 space-y-4">
            <h2 className="text-xl font-bold mb-4">Top Discoveries</h2>
            {insights.map((insight, index) => (
              <Card 
                key={insight.id}
                className={`cursor-pointer transition-all duration-200 ${
                  selectedInsight === index 
                    ? 'ring-2 ring-blue-500 shadow-lg' 
                    : 'hover:shadow-md'
                } bg-white/95 backdrop-blur-sm border-0`}
                onClick={() => setSelectedInsight(index)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="outline" className="text-xs">
                      {insight.confidence}% confidence
                    </Badge>
                    <TrendingUp className="w-4 h-4 text-green-500" />
                  </div>
                  <CardTitle className="text-lg">{insight.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 font-medium">
                    {insight.pattern}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Detailed View */}
          <div className="lg:col-span-2 space-y-6">
            {currentInsight && (
              <>
                <Card className="shadow-xl bg-white/95 backdrop-blur-sm border-0">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-2xl mb-2">{currentInsight.title}</CardTitle>
                        <CardDescription className="text-lg font-medium text-blue-600">
                          {currentInsight.pattern}
                        </CardDescription>
                      </div>
                      <Badge className="bg-green-100 text-green-800 text-sm px-3 py-1">
                        {currentInsight.confidence}% Confidence
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-6">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <h4 className="font-semibold mb-2 flex items-center">
                        <Target className="w-4 h-4 mr-2 text-blue-600" />
                        What This Means
                      </h4>
                      <p className="text-gray-700">{currentInsight.description}</p>
                    </div>

                    <div className="bg-green-50 rounded-lg p-4">
                      <h4 className="font-semibold mb-2 flex items-center">
                        <Clock className="w-4 h-4 mr-2 text-green-600" />
                        Actionable Insight
                      </h4>
                      <p className="text-gray-700">{currentInsight.actionable}</p>
                    </div>

                    <Separator />

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">{currentInsight.data_points}</div>
                        <div className="text-gray-500">Data Points</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">{currentInsight.correlation}</div>
                        <div className="text-gray-500">Correlation (r)</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Chart Section */}
                <Card className="shadow-xl bg-white/95 backdrop-blur-sm border-0">
                  <CardHeader>
                    <CardTitle>Pattern Visualization</CardTitle>
                    <CardDescription>
                      Your glucose response patterns over the analysis period
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <MetabolicChart />
                  </CardContent>
                </Card>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-4">
                  <Button 
                    onClick={handleShareInsights}
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                  >
                    <Share2 className="w-4 h-4 mr-2" />
                    Share Insights
                  </Button>
                  <Button variant="outline" onClick={handleDownloadReport}>
                    <Download className="w-4 h-4 mr-2" />
                    Download Report
                  </Button>
                  <Button variant="outline" onClick={onBack}>
                    Start New Analysis
                  </Button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

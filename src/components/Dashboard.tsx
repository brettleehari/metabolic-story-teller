
import { useState } from "react";
import { ArrowLeft, Sparkles, TrendingUp, Clock, Target, Share2, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import MetabolicChart from "@/components/MetabolicChart";

interface DashboardProps {
  onBack: () => void;
}

const Dashboard = ({ onBack }: DashboardProps) => {
  const [selectedInsight, setSelectedInsight] = useState(0);

  const insights = [
    {
      title: "Carb Timing Sweet Spot",
      pattern: "60% better glucose response to carbs before 2pm vs after 6pm",
      confidence: 87,
      description: "Your body processes carbohydrates significantly more efficiently in the earlier part of the day. This pattern was consistent across 12 of your 14 tracked days.",
      actionable: "Consider having your largest carb portions at breakfast and lunch, with lighter, protein-focused dinners.",
      dataPoints: 156,
      correlation: 0.72
    },
    {
      title: "Post-Lunch Walk Magic",
      pattern: "10-minute walks after lunch are 3x more effective than morning workouts",
      confidence: 92,
      description: "Short walks immediately after lunch consistently lowered your glucose peaks by an average of 35mg/dL compared to days without post-meal movement.",
      actionable: "Try incorporating brief 8-12 minute walks right after eating lunch for optimal glucose management.",
      dataPoints: 89,
      correlation: 0.68
    },
    {
      title: "Sleep Quality Impact",
      pattern: "Poor sleep makes dinner glucose spikes 40% higher",
      confidence: 79,
      description: "On nights when you slept less than 7 hours or had disrupted sleep, your evening meal responses were significantly more pronounced.",
      actionable: "Prioritize sleep hygiene, especially on days when you plan to have larger dinners or evening social meals.",
      dataPoints: 203,
      correlation: 0.58
    }
  ];

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
                key={index}
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
                    <div className="text-2xl font-bold text-blue-600">{currentInsight.dataPoints}</div>
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
              <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
                <Share2 className="w-4 h-4 mr-2" />
                Share Insights
              </Button>
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Download Report
              </Button>
              <Button variant="outline">
                Start New Analysis
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

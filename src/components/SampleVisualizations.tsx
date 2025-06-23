
import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, ReferenceLine } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TrendingUp, Clock, Moon, Utensils, Activity } from "lucide-react";

const SampleVisualizations = () => {
  const [activeChart, setActiveChart] = useState(0);

  const sampleInsights = [
    {
      title: "Carb Timing Sweet Spot",
      description: "60% better glucose response to carbs before 2pm",
      icon: Clock,
      color: "from-blue-500 to-cyan-500",
      data: [
        { time: "8am", earlyCarbs: 125, lateCarbs: 165 },
        { time: "10am", earlyCarbs: 140, lateCarbs: 180 },
        { time: "12pm", earlyCarbs: 110, lateCarbs: 155 },
        { time: "2pm", earlyCarbs: 105, lateCarbs: 170 },
        { time: "4pm", earlyCarbs: 100, lateCarbs: 175 },
        { time: "6pm", earlyCarbs: 120, lateCarbs: 190 },
        { time: "8pm", earlyCarbs: 130, lateCarbs: 195 }
      ]
    },
    {
      title: "Post-Meal Walk Impact",
      description: "10-minute walks reduce glucose spikes by 35mg/dL",
      icon: Activity,
      color: "from-green-500 to-emerald-500",
      data: [
        { meal: "Breakfast", withWalk: 125, withoutWalk: 160 },
        { meal: "Lunch", withWalk: 135, withoutWalk: 170 },
        { meal: "Dinner", withWalk: 145, withoutWalk: 180 },
        { meal: "Snack", withWalk: 115, withoutWalk: 150 }
      ]
    },
    {
      title: "Sleep Quality Effect",
      description: "Poor sleep increases dinner spikes by 40%",
      icon: Moon,
      color: "from-purple-500 to-pink-500",
      data: [
        { day: "Mon", goodSleep: 145, poorSleep: 185 },
        { day: "Tue", goodSleep: 140, poorSleep: 190 },
        { day: "Wed", goodSleep: 135, poorSleep: 175 },
        { day: "Thu", goodSleep: 150, poorSleep: 195 },
        { day: "Fri", goodSleep: 130, poorSleep: 180 },
        { day: "Sat", goodSleep: 155, poorSleep: 200 },
        { day: "Sun", goodSleep: 140, poorSleep: 185 }
      ]
    }
  ];

  const currentInsight = sampleInsights[activeChart];
  const Icon = currentInsight.icon;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value} mg/dL`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <Badge variant="outline" className="mb-4 px-4 py-2 text-sm font-medium">
            Sample Insights
          </Badge>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            See What You'll Discover
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Real examples of the personalized insights you'll receive from your data. 
            Each visualization reveals surprising patterns unique to your metabolism.
          </p>
        </div>

        <div className="max-w-6xl mx-auto">
          {/* Insight Selector */}
          <div className="flex flex-wrap justify-center gap-4 mb-8">
            {sampleInsights.map((insight, index) => {
              const InsightIcon = insight.icon;
              return (
                <Button
                  key={index}
                  variant={activeChart === index ? "default" : "outline"}
                  onClick={() => setActiveChart(index)}
                  className={`flex items-center gap-2 ${
                    activeChart === index 
                      ? `bg-gradient-to-r ${insight.color} text-white` 
                      : ''
                  }`}
                >
                  <InsightIcon className="w-4 h-4" />
                  {insight.title}
                </Button>
              );
            })}
          </div>

          {/* Main Visualization Card */}
          <Card className="shadow-2xl bg-gradient-to-br from-white to-gray-50 border-0">
            <CardHeader className="text-center pb-4">
              <div className={`w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br ${currentInsight.color} flex items-center justify-center`}>
                <Icon className="w-8 h-8 text-white" />
              </div>
              <CardTitle className="text-2xl mb-2">{currentInsight.title}</CardTitle>
              <CardDescription className="text-lg font-medium text-blue-600">
                {currentInsight.description}
              </CardDescription>
            </CardHeader>

            <CardContent className="pt-0">
              <div className="h-80 mb-6">
                <ResponsiveContainer width="100%" height="100%">
                  {activeChart === 1 ? (
                    <BarChart data={currentInsight.data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="meal" stroke="#666" fontSize={12} />
                      <YAxis stroke="#666" fontSize={12} domain={[100, 200]} />
                      <Tooltip content={<CustomTooltip />} />
                      <ReferenceLine y={140} stroke="#ff6b6b" strokeDasharray="2 2" />
                      <Bar dataKey="withWalk" fill="#10b981" name="With 10min Walk" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="withoutWalk" fill="#ef4444" name="Without Walk" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  ) : (
                    <LineChart data={currentInsight.data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey={activeChart === 0 ? "time" : "day"} 
                        stroke="#666" 
                        fontSize={12} 
                      />
                      <YAxis stroke="#666" fontSize={12} domain={[100, 220]} />
                      <Tooltip content={<CustomTooltip />} />
                      <ReferenceLine y={140} stroke="#ff6b6b" strokeDasharray="2 2" />
                      <Line 
                        type="monotone" 
                        dataKey={activeChart === 0 ? "earlyCarbs" : "goodSleep"} 
                        stroke="#10b981" 
                        strokeWidth={3}
                        dot={{ fill: '#10b981', strokeWidth: 2, r: 5 }}
                        name={activeChart === 0 ? "Early Carbs (Before 2pm)" : "Good Sleep (7+ hours)"}
                      />
                      <Line 
                        type="monotone" 
                        dataKey={activeChart === 0 ? "lateCarbs" : "poorSleep"} 
                        stroke="#ef4444" 
                        strokeWidth={3}
                        dot={{ fill: '#ef4444', strokeWidth: 2, r: 5 }}
                        name={activeChart === 0 ? "Late Carbs (After 6pm)" : "Poor Sleep (<6 hours)"}
                      />
                    </LineChart>
                  )}
                </ResponsiveContainer>
              </div>

              {/* Legend and Insights */}
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                    <span className="font-semibold text-green-800">Optimal Pattern</span>
                  </div>
                  <p className="text-sm text-green-700">
                    {activeChart === 0 && "Eating carbs earlier in the day leads to better glucose control"}
                    {activeChart === 1 && "Brief walks after meals significantly reduce glucose spikes"}
                    {activeChart === 2 && "Quality sleep improves your body's glucose response"}
                  </p>
                </div>

                <div className="bg-red-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                    <span className="font-semibold text-red-800">Pattern to Avoid</span>
                  </div>
                  <p className="text-sm text-red-700">
                    {activeChart === 0 && "Late evening carbs create larger, longer-lasting glucose spikes"}
                    {activeChart === 1 && "Sitting after meals allows glucose to stay elevated longer"}
                    {activeChart === 2 && "Poor sleep makes your body less efficient at processing glucose"}
                  </p>
                </div>
              </div>

              {/* Sample Narrative */}
              <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-l-4 border-blue-400">
                <div className="flex items-start">
                  <TrendingUp className="w-5 h-5 text-blue-600 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-blue-900 mb-2">Your Personal Insight</h4>
                    <p className="text-blue-800 text-sm leading-relaxed">
                      "We discovered something interesting about your metabolism: 
                      {activeChart === 0 && " your body processes carbohydrates 60% more efficiently when you eat them before 2pm compared to after 6pm. This pattern was consistent across 12 of your 14 tracked days."}
                      {activeChart === 1 && " taking just a 10-minute walk after meals reduces your glucose peaks by an average of 35mg/dL. This simple habit was more effective than longer morning workouts."}
                      {activeChart === 2 && " the quality of your sleep has a dramatic impact on how your body handles dinner. On nights with poor sleep, your evening glucose spikes were 40% higher."}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Call to Action */}
          <div className="text-center mt-8">
            <p className="text-gray-600 mb-4">
              Ready to discover your unique patterns?
            </p>
            <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-lg px-8 py-3">
              Upload Your Data & Get Started
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SampleVisualizations;

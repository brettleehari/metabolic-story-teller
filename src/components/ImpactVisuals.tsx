
import { useState, useEffect } from "react";
import { Moon, Utensils, Dumbbell, Heart, TrendingUp, TrendingDown } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const ImpactVisuals = () => {
  const [activeAnimation, setActiveAnimation] = useState(0);

  const impacts = [
    {
      icon: Moon,
      title: "Sleep Quality",
      positive: "Good Sleep (7+ hours)",
      negative: "Poor Sleep (<6 hours)",
      positiveEffect: "Stable glucose, better insulin sensitivity",
      negativeEffect: "40% higher dinner spikes, irregular patterns",
      color: "from-indigo-400 to-purple-500"
    },
    {
      icon: Utensils,
      title: "Meal Timing",
      positive: "Early Carbs (Before 2pm)",
      negative: "Late Carbs (After 6pm)", 
      positiveEffect: "60% better glucose response",
      negativeEffect: "Higher spikes, slower recovery",
      color: "from-orange-400 to-red-500"
    },
    {
      icon: Dumbbell,
      title: "Exercise Timing",
      positive: "Post-Meal Walk (10 min)",
      negative: "No Movement",
      positiveEffect: "35mg/dL lower glucose peaks",
      negativeEffect: "Extended glucose elevation",
      color: "from-green-400 to-emerald-500"
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveAnimation((prev) => (prev + 1) % impacts.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="py-16 bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">See How Your Body Responds</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Watch how different lifestyle factors create unique patterns in your metabolic response
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {impacts.map((impact, index) => {
            const Icon = impact.icon;
            const isActive = activeAnimation === index;
            
            return (
              <Card 
                key={index}
                className={`relative overflow-hidden transition-all duration-500 cursor-pointer ${
                  isActive ? 'scale-105 shadow-2xl ring-2 ring-blue-400' : 'hover:scale-102 shadow-lg'
                }`}
                onClick={() => setActiveAnimation(index)}
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${impact.color} opacity-5`} />
                
                <CardContent className="p-6">
                  <div className="text-center mb-6">
                    <div className={`w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br ${impact.color} flex items-center justify-center transform transition-all duration-300 ${
                      isActive ? 'scale-110 animate-pulse' : ''
                    }`}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-bold">{impact.title}</h3>
                  </div>

                  {/* Animated Comparison */}
                  <div className="space-y-4">
                    {/* Positive Impact */}
                    <div className={`p-3 rounded-lg bg-green-50 border-l-4 border-green-400 transition-all duration-500 ${
                      isActive ? 'translate-x-0 opacity-100' : 'translate-x-2 opacity-70'
                    }`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-green-800">{impact.positive}</span>
                        <TrendingUp className={`w-4 h-4 text-green-600 transition-transform duration-300 ${
                          isActive ? 'scale-110' : ''
                        }`} />
                      </div>
                      <p className="text-xs text-green-700">{impact.positiveEffect}</p>
                    </div>

                    {/* Negative Impact */}
                    <div className={`p-3 rounded-lg bg-red-50 border-l-4 border-red-400 transition-all duration-500 ${
                      isActive ? 'translate-x-0 opacity-100' : 'translate-x-2 opacity-70'
                    }`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-red-800">{impact.negative}</span>
                        <TrendingDown className={`w-4 h-4 text-red-600 transition-transform duration-300 ${
                          isActive ? 'scale-110' : ''
                        }`} />
                      </div>
                      <p className="text-xs text-red-700">{impact.negativeEffect}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Animated Body Visualization */}
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-4xl mx-auto">
          <h3 className="text-2xl font-bold text-center mb-8">Your Body's Response Timeline</h3>
          
          <div className="relative">
            {/* Timeline */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex-1 h-2 bg-gradient-to-r from-blue-200 via-purple-200 to-green-200 rounded-full relative">
                <div 
                  className="absolute top-0 left-0 h-2 bg-gradient-to-r from-blue-500 via-purple-500 to-green-500 rounded-full transition-all duration-1000"
                  style={{ width: `${((activeAnimation + 1) / 3) * 100}%` }}
                />
              </div>
            </div>

            {/* Body Impact Visualization */}
            <div className="grid md:grid-cols-3 gap-8 text-center">
              <div className={`transition-all duration-500 ${activeAnimation === 0 ? 'scale-110' : 'opacity-60'}`}>
                <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center">
                  <Heart className="w-10 h-10 text-white animate-pulse" />
                </div>
                <p className="font-semibold">Sleep Impact</p>
                <p className="text-sm text-gray-600">Affects next day's insulin sensitivity</p>
              </div>

              <div className={`transition-all duration-500 ${activeAnimation === 1 ? 'scale-110' : 'opacity-60'}`}>
                <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center">
                  <TrendingUp className="w-10 h-10 text-white animate-bounce" />
                </div>
                <p className="font-semibold">Meal Response</p>
                <p className="text-sm text-gray-600">Glucose spike within 30-90 minutes</p>
              </div>

              <div className={`transition-all duration-500 ${activeAnimation === 2 ? 'scale-110' : 'opacity-60'}`}>
                <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center">
                  <Dumbbell className="w-10 h-10 text-white animate-pulse" />
                </div>
                <p className="font-semibold">Exercise Effect</p>
                <p className="text-sm text-gray-600">Immediate glucose uptake boost</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ImpactVisuals;

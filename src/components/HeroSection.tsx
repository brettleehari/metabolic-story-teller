
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface HeroSectionProps {
  onGetStarted: () => void;
}

const HeroSection = ({ onGetStarted }: HeroSectionProps) => {
  return (
    <section className="text-center py-20">
      <Badge variant="outline" className="mb-6 px-4 py-2 text-sm font-medium bg-white/50 backdrop-blur-sm">
        <Sparkles className="w-4 h-4 mr-2" />
        AI-Powered Metabolic Insights
      </Badge>
      
      <h1 className="text-6xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
        Discover Your
        <span className="block bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
          Hidden Patterns
        </span>
      </h1>
      
      <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
        Upload your glucose, sleep, food, and exercise data to uncover surprising insights 
        about how <strong>YOUR</strong> body uniquely responds. Get personalized metabolic patterns 
        you couldn't discover manually.
      </p>
      
      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
        <Button 
          size="lg" 
          onClick={onGetStarted}
          className="px-8 py-4 text-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
        >
          Start Your Analysis
          <ArrowRight className="ml-2 w-5 h-5" />
        </Button>
        
        <Button 
          variant="outline" 
          size="lg"
          className="px-8 py-4 text-lg border-2 hover:bg-white/50 backdrop-blur-sm"
        >
          See Sample Results
        </Button>
      </div>
      
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-2xl p-8 max-w-4xl mx-auto">
        <div className="grid md:grid-cols-2 gap-8 items-center">
          <div className="text-left">
            <h3 className="text-2xl font-bold mb-4">Example Insight</h3>
            <blockquote className="text-gray-700 italic text-lg leading-relaxed">
              "We discovered something surprising: your glucose responds 60% better to carbs 
              before 2pm versus after 6pm. Additionally, 10-minute post-lunch walks are 3x 
              more effective for you than morning workouts."
            </blockquote>
            <div className="mt-4 text-sm text-gray-500">
              - From Sarah's Metabolic Story
            </div>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-indigo-600 mb-2">85%</div>
              <div className="text-sm text-gray-600 mb-4">Pattern Confidence</div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2 rounded-full" style={{ width: '85%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

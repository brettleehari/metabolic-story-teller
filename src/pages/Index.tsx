
import { useState } from "react";
import { Upload, Brain, TrendingUp, Users, ArrowRight, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import HeroSection from "@/components/HeroSection";
import FeatureCard from "@/components/FeatureCard";
import UploadWizard from "@/components/UploadWizard";
import Dashboard from "@/components/Dashboard";
import AuthForm from "@/components/AuthForm";
import ImpactVisuals from "@/components/ImpactVisuals";
import SampleVisualizations from "@/components/SampleVisualizations";

const Index = () => {
  const [currentView, setCurrentView] = useState<'landing' | 'auth' | 'upload' | 'dashboard'>('landing');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const features = [
    {
      icon: Upload,
      title: "Multi-Modal Data Upload",
      description: "Upload CGM, sleep, food, and exercise data from various sources. Flexible CSV parsing handles different export formats.",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: Brain,
      title: "AI Pattern Discovery",
      description: "Advanced statistical analysis discovers surprising correlations you couldn't find manually. Counter-intuitive insights prioritized.",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: TrendingUp,
      title: "Personal Metabolic Story",
      description: "AI-generated narratives transform complex data into engaging, personalized insights about your unique patterns.",
      color: "from-green-500 to-emerald-500"
    }
  ];

  const handleGetStarted = () => {
    if (isAuthenticated) {
      setCurrentView('upload');
    } else {
      setCurrentView('auth');
    }
  };

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
    setCurrentView('upload');
  };

  const handleUploadComplete = () => {
    setCurrentView('dashboard');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'auth':
        return <AuthForm onSuccess={handleAuthSuccess} onBack={() => setCurrentView('landing')} />;
      case 'upload':
        return <UploadWizard onComplete={handleUploadComplete} onBack={() => setCurrentView('landing')} />;
      case 'dashboard':
        return <Dashboard onBack={() => setCurrentView('landing')} />;
      default:
        return (
          <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
            <div className="container mx-auto px-4 py-8">
              <HeroSection onGetStarted={handleGetStarted} />
              
              {/* Impact Visuals Section */}
              <ImpactVisuals />
              
              {/* Sample Visualizations Section - NEW */}
              <SampleVisualizations />
              
              {/* Features Section */}
              <section className="py-20">
                <div className="text-center mb-16">
                  <Badge variant="outline" className="mb-4 px-4 py-2 text-sm font-medium">
                    How It Works
                  </Badge>
                  <h2 className="text-4xl font-bold text-gray-900 mb-4">
                    Discover Your Hidden Metabolic Patterns
                  </h2>
                  <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                    Upload 14 days of health data and get AI-powered insights about surprising patterns 
                    in how YOUR body responds to food, sleep, and exercise.
                  </p>
                </div>
                
                <div className="grid md:grid-cols-3 gap-8 mb-16">
                  {features.map((feature, index) => (
                    <FeatureCard key={index} {...feature} />
                  ))}
                </div>

                {/* Process Steps */}
                <div className="bg-white rounded-2xl shadow-xl p-8 mb-16">
                  <h3 className="text-2xl font-bold text-center mb-8">Simple 3-Step Process</h3>
                  <div className="grid md:grid-cols-3 gap-8">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Upload className="w-8 h-8 text-blue-600" />
                      </div>
                      <h4 className="font-semibold mb-2">1. Upload Your Data</h4>
                      <p className="text-gray-600">Upload CSV files from your CGM, sleep tracker, food log, and exercise data</p>
                    </div>
                    <div className="text-center">
                      <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Brain className="w-8 h-8 text-purple-600" />
                      </div>
                      <h4 className="font-semibold mb-2">2. AI Analysis</h4>
                      <p className="text-gray-600">Our engine discovers statistical correlations and surprising patterns</p>
                    </div>
                    <div className="text-center">
                      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <TrendingUp className="w-8 h-8 text-green-600" />
                      </div>
                      <h4 className="font-semibold mb-2">3. Get Insights</h4>
                      <p className="text-gray-600">Receive your personalized metabolic story with actionable insights</p>
                    </div>
                  </div>
                </div>

                {/* Stats Section */}
                <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl text-white p-8 text-center">
                  <h3 className="text-2xl font-bold mb-8">Powered by Advanced Analytics</h3>
                  <div className="grid md:grid-cols-4 gap-8">
                    <div>
                      <div className="text-3xl font-bold mb-2">70%+</div>
                      <div className="text-indigo-200">Data Completeness Required</div>
                    </div>
                    <div>
                      <div className="text-3xl font-bold mb-2">r ≥ 0.5</div>
                      <div className="text-indigo-200">Correlation Threshold</div>
                    </div>
                    <div>
                      <div className="text-3xl font-bold mb-2">p &lt; 0.05</div>
                      <div className="text-indigo-200">Statistical Significance</div>
                    </div>
                    <div>
                      <div className="text-3xl font-bold mb-2">14+</div>
                      <div className="text-indigo-200">Days Minimum Data</div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen">
      {renderCurrentView()}
    </div>
  );
};

export default Index;

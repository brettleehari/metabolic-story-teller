import { useState } from "react";
import { Upload, FileText, Activity, Moon, UtensilsCrossed, ArrowLeft, ArrowRight, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { uploadService } from "@/services/uploadService";
import { analysisService } from "@/services/analysisService";
import { useToast } from "@/hooks/use-toast";

interface UploadWizardProps {
  onComplete: () => void;
  onBack: () => void;
}

const UploadWizard = ({ onComplete, onBack }: UploadWizardProps) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState<Record<string, { file_id: string; file: File }>>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [analysisJobId, setAnalysisJobId] = useState<string | null>(null);
  const { toast } = useToast();

  const dataTypes = [
    {
      id: 'glucose',
      title: 'Glucose Data',
      description: 'CGM readings from Dexcom, Abbott, or manual entries',
      icon: Activity,
      color: 'from-red-500 to-pink-500',
      sampleFields: ['timestamp', 'glucose_value', 'data_source'],
      requirements: 'Minimum 14 days, readings every 15 minutes preferred'
    },
    {
      id: 'sleep',
      title: 'Sleep Data',
      description: 'Duration, quality, and timing from wearables or apps',
      icon: Moon,
      color: 'from-indigo-500 to-purple-500',
      sampleFields: ['date', 'bedtime', 'waketime', 'duration_hours', 'quality_score'],
      requirements: 'Daily sleep records for 14+ days'
    },
    {
      id: 'food',
      title: 'Food Entries',
      description: 'Meal timing and descriptions from food logs',
      icon: UtensilsCrossed,
      color: 'from-green-500 to-emerald-500',
      sampleFields: ['timestamp', 'meal_description', 'notes'],
      requirements: 'Meals with timing for correlation analysis'
    },
    {
      id: 'exercise',
      title: 'Exercise Data',
      description: 'Activity type, duration, and intensity tracking',
      icon: FileText,
      color: 'from-orange-500 to-red-500',
      sampleFields: ['timestamp', 'activity_type', 'duration_minutes', 'intensity'],
      requirements: 'Exercise sessions with timing and intensity'
    }
  ];

  const handleFileUpload = async (dataType: string, file: File) => {
    try {
      const response = await uploadService.uploadFile({
        file,
        data_type: dataType as 'glucose' | 'sleep' | 'food' | 'exercise',
      });

      if (response.success && response.file_id) {
        setUploadedFiles(prev => ({ 
          ...prev, 
          [dataType]: { file_id: response.file_id!, file } 
        }));
        
        toast({
          title: "File uploaded successfully!",
          description: `${dataType} data has been processed and validated.`,
        });
      } else {
        throw new Error(response.message || "Upload failed");
      }
    } catch (error) {
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Failed to upload file",
        variant: "destructive",
      });
    }
  };

  const handleFileSelect = (dataType: string) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        handleFileUpload(dataType, file);
      }
    };
    input.click();
  };

  const handleNext = () => {
    if (currentStep < dataTypes.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      startProcessing();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const startProcessing = async () => {
    setIsProcessing(true);
    setProcessingProgress(0);
    
    try {
      const fileIds = Object.values(uploadedFiles).map(upload => upload.file_id);
      const response = await analysisService.startAnalysis({ file_ids: fileIds });
      
      setAnalysisJobId(response.job_id);
      
      // Poll for analysis status
      const pollInterval = setInterval(async () => {
        try {
          const status = await analysisService.getAnalysisStatus(response.job_id);
          
          setProcessingProgress(status.progress || 0);
          
          if (status.status === 'completed') {
            clearInterval(pollInterval);
            toast({
              title: "Analysis complete!",
              description: "Your personalized insights are ready.",
            });
            onComplete();
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            throw new Error(status.message || "Analysis failed");
          }
        } catch (error) {
          clearInterval(pollInterval);
          throw error;
        }
      }, 2000);
      
    } catch (error) {
      setIsProcessing(false);
      toast({
        title: "Analysis failed",
        description: error instanceof Error ? error.message : "Failed to start analysis",
        variant: "destructive",
      });
    }
  };

  const currentDataType = dataTypes[currentStep];
  const progress = ((Object.keys(uploadedFiles).length) / dataTypes.length) * 100;
  const canProceed = Object.keys(uploadedFiles).length >= 2; // Minimum 2 data types

  if (isProcessing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-2xl bg-white/95 backdrop-blur-sm border-0">
          <CardHeader className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center animate-pulse">
              <Activity className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold">Processing Your Data</CardTitle>
            <CardDescription>Our AI is analyzing your patterns...</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Analysis Progress</span>
                <span>{Math.round(processingProgress)}%</span>
              </div>
              <Progress value={processingProgress} className="h-2" />
            </div>
            {analysisJobId && (
              <div className="text-xs text-gray-500 text-center">
                Job ID: {analysisJobId}
              </div>
            )}
            <div className="text-center text-sm text-gray-600">
              This may take a few minutes. You'll be redirected when complete.
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4">
      <div className="container mx-auto max-w-4xl">
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
            <h1 className="text-3xl font-bold mb-4">Upload Your Health Data</h1>
            <p className="text-gray-600 mb-6">
              Upload CSV files for each data type. We need at least 2 types with 14+ days of data.
            </p>
            <Progress value={progress} className="max-w-md mx-auto" />
            <div className="text-sm text-gray-500 mt-2">
              {Object.keys(uploadedFiles).length} of {dataTypes.length} files uploaded
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Current Step */}
          <Card className="shadow-xl bg-white/95 backdrop-blur-sm border-0">
            <CardHeader>
              <div className={`w-12 h-12 mb-4 rounded-lg bg-gradient-to-br ${currentDataType.color} flex items-center justify-center`}>
                <currentDataType.icon className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="flex items-center justify-between">
                {currentDataType.title}
                {uploadedFiles[currentDataType.id] && (
                  <Badge className="bg-green-100 text-green-800">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Uploaded
                  </Badge>
                )}
              </CardTitle>
              <CardDescription>{currentDataType.description}</CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              <div>
                <h4 className="font-semibold mb-2">Expected CSV Format:</h4>
                <div className="bg-gray-50 rounded-lg p-3">
                  <code className="text-sm text-gray-700">
                    {currentDataType.sampleFields.join(', ')}
                  </code>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Requirements:</h4>
                <p className="text-sm text-gray-600">{currentDataType.requirements}</p>
              </div>

              <div 
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
                onClick={() => handleFileSelect(currentDataType.id)}
              >
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">
                  {uploadedFiles[currentDataType.id] 
                    ? `File uploaded: ${uploadedFiles[currentDataType.id].file.name}` 
                    : "Click to upload CSV file"
                  }
                </p>
                <Button 
                  variant={uploadedFiles[currentDataType.id] ? "outline" : "default"}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleFileSelect(currentDataType.id);
                  }}
                >
                  {uploadedFiles[currentDataType.id] ? "Re-upload" : "Choose File"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Progress Overview */}
          <Card className="shadow-xl bg-white/95 backdrop-blur-sm border-0">
            <CardHeader>
              <CardTitle>Upload Progress</CardTitle>
              <CardDescription>Track your data upload across all types</CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              {dataTypes.map((dataType, index) => (
                <div 
                  key={dataType.id}
                  className={`flex items-center p-3 rounded-lg transition-all cursor-pointer ${
                    index === currentStep 
                      ? 'bg-blue-50 border-2 border-blue-200' 
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                  onClick={() => setCurrentStep(index)}
                >
                  <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${dataType.color} flex items-center justify-center mr-3`}>
                    <dataType.icon className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">{dataType.title}</div>
                  </div>
                  {uploadedFiles[dataType.id] && (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  )}
                </div>
              ))}

              <div className="pt-4 border-t">
                <div className="flex justify-between gap-3">
                  <Button 
                    variant="outline" 
                    onClick={handlePrevious}
                    disabled={currentStep === 0}
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Previous
                  </Button>
                  
                  {currentStep === dataTypes.length - 1 ? (
                    <Button 
                      onClick={startProcessing}
                      disabled={!canProceed}
                      className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                    >
                      Start Analysis
                      <Activity className="w-4 h-4 ml-2" />
                    </Button>
                  ) : (
                    <Button onClick={handleNext}>
                      Next
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  )}
                </div>
                
                {!canProceed && (
                  <p className="text-sm text-gray-500 mt-2 text-center">
                    Upload at least 2 data types to proceed
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UploadWizard;

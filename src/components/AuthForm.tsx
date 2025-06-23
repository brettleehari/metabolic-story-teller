
import { useState } from "react";
import { Mail, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface AuthFormProps {
  onSuccess: () => void;
  onBack: () => void;
}

const AuthForm = ({ onSuccess, onBack }: AuthFormProps) => {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setEmailSent(true);
      
      // Simulate magic link click after 3 seconds
      setTimeout(() => {
        onSuccess();
      }, 3000);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Button 
          variant="ghost" 
          onClick={onBack} 
          className="mb-6 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Home
        </Button>

        <Card className="shadow-2xl bg-white/95 backdrop-blur-sm border-0">
          <CardHeader className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
              <Mail className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold">
              {emailSent ? "Check Your Email" : "Sign In to Gluco-Lens"}
            </CardTitle>
            <CardDescription className="text-gray-600">
              {emailSent 
                ? "We've sent you a magic link to sign in securely"
                : "We'll send you a secure magic link - no password needed"
              }
            </CardDescription>
          </CardHeader>

          <CardContent>
            {!emailSent ? (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <Input
                    type="email"
                    placeholder="Enter your email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="h-12 text-lg"
                  />
                </div>

                <Button 
                  type="submit" 
                  disabled={isLoading || !email}
                  className="w-full h-12 text-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                >
                  {isLoading ? "Sending Magic Link..." : "Send Magic Link"}
                </Button>

                <div className="text-center text-sm text-gray-500">
                  <p>✨ Secure, passwordless authentication</p>
                  <p>🔒 Your data is encrypted and private</p>
                </div>
              </form>
            ) : (
              <div className="text-center space-y-6">
                <div className="animate-pulse">
                  <Badge variant="outline" className="px-4 py-2 text-sm">
                    Magic link sent to {email}
                  </Badge>
                </div>
                
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-2">
                    Click the link in your email to sign in instantly
                  </p>
                  <div className="text-xs text-gray-500">
                    Demo: Auto-signing you in...
                  </div>
                </div>

                <Button 
                  variant="outline"
                  onClick={() => setEmailSent(false)}
                  className="text-sm text-gray-600"
                >
                  Try different email
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AuthForm;

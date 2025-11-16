// Demo Index Page - Profile Selection for Read-Only Demo
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DEMO_USERS, DemoUser } from '@/config/demo';
import { Activity, TrendingDown, TrendingUp, Moon, Heart, Zap } from 'lucide-react';

export const DemoIndex = () => {
  const navigate = useNavigate();
  const [selectedUser, setSelectedUser] = useState<string | null>(null);

  const handleSelectUser = (userId: string) => {
    setSelectedUser(userId);
    // Store selected demo user in sessionStorage
    sessionStorage.setItem('demo_user_id', userId);
    // Navigate to dashboard
    setTimeout(() => {
      navigate(`/demo/dashboard/${userId}`);
    }, 300);
  };

  const getProfileBadgeVariant = (profile: DemoUser['profile']) => {
    switch (profile) {
      case 'well_controlled':
        return 'default';
      case 'variable':
        return 'secondary';
      case 'active':
        return 'outline';
      default:
        return 'default';
    }
  };

  const getProfileIcon = (profile: DemoUser['profile']) => {
    switch (profile) {
      case 'well_controlled':
        return <Heart className="h-5 w-5 text-green-600" />;
      case 'variable':
        return <TrendingUp className="h-5 w-5 text-orange-600" />;
      case 'active':
        return <Zap className="h-5 w-5 text-blue-600" />;
      default:
        return <Activity className="h-5 w-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">GlucoLens Demo</h1>
              <p className="mt-1 text-sm text-gray-600">
                Interactive read-only demo with pre-loaded user profiles
              </p>
            </div>
            <Badge variant="outline" className="text-blue-600 border-blue-600">
              Read-Only Demo
            </Badge>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Introduction */}
        <div className="text-center mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Choose a Demo Profile to Explore
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Each profile represents a different glucose management journey with 90 days of data,
            including continuous glucose monitoring, sleep patterns, meals, and exercise activities.
            All insights are pre-computed using advanced ML analytics (PCMCI, STUMPY).
          </p>
        </div>

        {/* Demo User Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {DEMO_USERS.map((user) => (
            <Card
              key={user.id}
              className={`cursor-pointer transition-all duration-300 hover:shadow-xl hover:scale-105 ${
                selectedUser === user.id ? 'ring-2 ring-blue-500 shadow-xl' : ''
              }`}
              onClick={() => handleSelectUser(user.id)}
            >
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    {/* Avatar */}
                    <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
                      {user.avatar}
                    </div>
                    <div>
                      <CardTitle className="text-xl">{user.fullName}</CardTitle>
                      <CardDescription>{user.age} years old</CardDescription>
                    </div>
                  </div>
                  {getProfileIcon(user.profile)}
                </div>
                <Badge variant={getProfileBadgeVariant(user.profile)} className="w-fit">
                  {user.profile.replace('_', ' ').toUpperCase()}
                </Badge>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Description */}
                <p className="text-sm text-gray-600">{user.description}</p>

                {/* Key Stats */}
                <div className="grid grid-cols-2 gap-3 pt-2 border-t">
                  <div>
                    <p className="text-xs text-gray-500">Avg Glucose</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {user.stats.avgGlucose} mg/dL
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Time in Range</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {user.stats.timeInRange}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">HbA1c</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {user.stats.hba1c}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Sleep Quality</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {user.stats.sleepQuality}%
                    </p>
                  </div>
                </div>

                {/* Characteristics */}
                <div className="pt-2 border-t">
                  <p className="text-xs font-semibold text-gray-700 mb-2">Key Characteristics:</p>
                  <ul className="space-y-1">
                    {user.characteristics.slice(0, 3).map((char, idx) => (
                      <li key={idx} className="text-xs text-gray-600 flex items-start">
                        <span className="text-blue-600 mr-1">•</span>
                        <span>{char}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Action Button */}
                <Button
                  className="w-full mt-4"
                  variant={selectedUser === user.id ? 'default' : 'outline'}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSelectUser(user.id);
                  }}
                >
                  {selectedUser === user.id ? 'Loading Dashboard...' : 'View Dashboard'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Features Section */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">
            What's Included in This Demo
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full h-12 w-12 flex items-center justify-center mx-auto mb-3">
                <Activity className="h-6 w-6 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">90 Days of Data</h4>
              <p className="text-sm text-gray-600">
                Glucose readings every 5 minutes, daily sleep, meals, and activities
              </p>
            </div>

            <div className="text-center">
              <div className="bg-purple-100 rounded-full h-12 w-12 flex items-center justify-center mx-auto mb-3">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">ML Analytics</h4>
              <p className="text-sm text-gray-600">
                PCMCI causal discovery, STUMPY pattern detection, association rules
              </p>
            </div>

            <div className="text-center">
              <div className="bg-green-100 rounded-full h-12 w-12 flex items-center justify-center mx-auto mb-3">
                <Moon className="h-6 w-6 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">Lifestyle Factors</h4>
              <p className="text-sm text-gray-600">
                Sleep quality, exercise impact, meal timing, and stress patterns
              </p>
            </div>

            <div className="text-center">
              <div className="bg-orange-100 rounded-full h-12 w-12 flex items-center justify-center mx-auto mb-3">
                <Zap className="h-6 w-6 text-orange-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">Real-Time Insights</h4>
              <p className="text-sm text-gray-600">
                Interactive charts, correlation analysis, and personalized recommendations
              </p>
            </div>
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            This is a read-only demo with synthetic data. No authentication required.
          </p>
          <p className="mt-1">
            Powered by AWS Lambda, Aurora Serverless, and CloudFront CDN.
          </p>
        </div>
      </div>
    </div>
  );
};

export default DemoIndex;

// Demo Dashboard Page - Read-Only Dashboard for Demo Users
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { getDemoUserById } from '@/config/demo';
import {
  demoService,
  DashboardData,
  Correlation,
  Pattern,
} from '@/services/demoService';
import { ArrowLeft, TrendingUp, TrendingDown, Activity, Moon, Utensils, Dumbbell } from 'lucide-react';
import { toast } from 'sonner';

export const DemoDashboard = () => {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState<'7' | '30' | '90'>('30');
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);

  const user = userId ? getDemoUserById(userId) : null;

  useEffect(() => {
    if (!user || !userId) {
      toast.error('Invalid demo user');
      navigate('/demo');
      return;
    }

    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const data = await demoService.getDashboard(userId, period);
        setDashboardData(data);
      } catch (error) {
        console.error('Error fetching dashboard:', error);
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [userId, period, user, navigate]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  const getCorrelationIcon = (factorType: string) => {
    switch (factorType) {
      case 'sleep':
        return <Moon className="h-4 w-4" />;
      case 'exercise':
        return <Dumbbell className="h-4 w-4" />;
      case 'meal':
        return <Utensils className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const formatCorrelation = (value: number): string => {
    return value >= 0 ? `+${value.toFixed(3)}` : value.toFixed(3);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/demo')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Profiles
              </Button>
              <div className="border-l pl-4">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                    {user.avatar}
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-gray-900">{user.fullName}</h1>
                    <p className="text-sm text-gray-600">{user.description}</p>
                  </div>
                </div>
              </div>
            </div>
            <Badge variant="outline" className="text-blue-600 border-blue-600">
              Read-Only Demo
            </Badge>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Period Selector */}
        <div className="mb-6">
          <Tabs value={period} onValueChange={(v) => setPeriod(v as '7' | '30' | '90')}>
            <TabsList>
              <TabsTrigger value="7">Last 7 Days</TabsTrigger>
              <TabsTrigger value="30">Last 30 Days</TabsTrigger>
              <TabsTrigger value="90">Last 90 Days</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <p className="text-gray-600">Loading dashboard data...</p>
          </div>
        ) : dashboardData ? (
          <div className="space-y-6">
            {/* Glucose Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Average Glucose</CardDescription>
                  <CardTitle className="text-3xl">
                    {dashboardData.glucose_stats.avg.toFixed(0)}
                    <span className="text-lg text-gray-500 ml-1">mg/dL</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center text-sm text-gray-600">
                    <Activity className="h-4 w-4 mr-1" />
                    Range: {dashboardData.glucose_stats.min.toFixed(0)} - {dashboardData.glucose_stats.max.toFixed(0)}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Time in Range</CardDescription>
                  <CardTitle className="text-3xl text-green-600">
                    {dashboardData.glucose_stats.time_in_range_70_180.toFixed(0)}%
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-gray-600">
                    Target: 70-180 mg/dL
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Time Below Range</CardDescription>
                  <CardTitle className="text-3xl text-orange-600">
                    {dashboardData.glucose_stats.time_below_70.toFixed(1)}%
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-gray-600">
                    Below 70 mg/dL
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Time Above Range</CardDescription>
                  <CardTitle className="text-3xl text-red-600">
                    {dashboardData.glucose_stats.time_above_180.toFixed(1)}%
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-gray-600">
                    Above 180 mg/dL
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Correlations */}
            <Card>
              <CardHeader>
                <CardTitle>Top Correlations</CardTitle>
                <CardDescription>
                  Lifestyle factors most strongly correlated with glucose levels
                </CardDescription>
              </CardHeader>
              <CardContent>
                {dashboardData.correlations.length > 0 ? (
                  <div className="space-y-3">
                    {dashboardData.correlations.slice(0, 8).map((corr, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                      >
                        <div className="flex items-center space-x-3">
                          {getCorrelationIcon(corr.factor_type)}
                          <div>
                            <p className="font-medium text-gray-900">{corr.factor_name}</p>
                            <p className="text-sm text-gray-600">{corr.interpretation}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {corr.correlation >= 0 ? (
                            <TrendingUp className="h-5 w-5 text-red-500" />
                          ) : (
                            <TrendingDown className="h-5 w-5 text-green-500" />
                          )}
                          <Badge variant={corr.abs_correlation > 0.5 ? 'default' : 'secondary'}>
                            {formatCorrelation(corr.correlation)}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600 text-center py-8">
                    No significant correlations found for this period
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Patterns */}
            <Card>
              <CardHeader>
                <CardTitle>Discovered Patterns</CardTitle>
                <CardDescription>
                  Association rules showing lifestyle patterns that affect glucose
                </CardDescription>
              </CardHeader>
              <CardContent>
                {dashboardData.patterns.length > 0 ? (
                  <div className="space-y-3">
                    {dashboardData.patterns.slice(0, 6).map((pattern, idx) => (
                      <div
                        key={idx}
                        className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <p className="text-sm text-gray-600">
                              <span className="font-semibold">When:</span>{' '}
                              {pattern.antecedents.join(' + ')}
                            </p>
                            <p className="text-sm text-gray-600 mt-1">
                              <span className="font-semibold">Then:</span>{' '}
                              {pattern.consequents.join(' + ')}
                            </p>
                          </div>
                          <div className="flex flex-col items-end space-y-1 ml-4">
                            <Badge variant="outline">
                              {(pattern.confidence * 100).toFixed(0)}% confidence
                            </Badge>
                            <Badge variant="secondary">
                              {pattern.lift.toFixed(1)}x lift
                            </Badge>
                          </div>
                        </div>
                        <p className="text-sm text-gray-700 italic mt-2">
                          {pattern.interpretation}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600 text-center py-8">
                    No significant patterns found for this period
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Info Footer */}
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-6">
                <p className="text-sm text-blue-900">
                  <strong>Note:</strong> This is a read-only demo with pre-computed insights.
                  All data is synthetic and generated for demonstration purposes. The ML analytics
                  (PCMCI causal discovery, STUMPY pattern detection, and association rule mining)
                  are running on real data but represent a simulated user profile.
                </p>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="flex items-center justify-center py-12">
            <p className="text-gray-600">No data available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DemoDashboard;

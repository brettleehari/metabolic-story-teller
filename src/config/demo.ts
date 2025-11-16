// Demo Mode Configuration for AWS Lambda Read-Only Demo

export interface DemoUser {
  id: string;
  email: string;
  fullName: string;
  age: number;
  profile: 'well_controlled' | 'variable' | 'active';
  description: string;
  characteristics: string[];
  avatar: string;
  stats: {
    avgGlucose: number;
    timeInRange: number;
    hba1c: number;
    sleepQuality: number;
  };
}

// Demo user profiles matching backend generate_demo_users.py
export const DEMO_USERS: DemoUser[] = [
  {
    id: '11111111-1111-1111-1111-111111111111',
    email: 'alice@demo.glucolens.com',
    fullName: 'Alice Thompson',
    age: 34,
    profile: 'well_controlled',
    description: 'Well-controlled glucose with consistent lifestyle patterns',
    characteristics: [
      'Excellent glucose control (avg 105 mg/dL)',
      'High time in range (85%)',
      'Consistent sleep patterns (7-8 hours)',
      'Regular meal timing',
      'Moderate exercise routine',
      'Low glucose variability'
    ],
    avatar: 'AT',
    stats: {
      avgGlucose: 105,
      timeInRange: 85,
      hba1c: 5.8,
      sleepQuality: 85
    }
  },
  {
    id: '22222222-2222-2222-2222-222222222222',
    email: 'bob@demo.glucolens.com',
    fullName: 'Bob Martinez',
    age: 45,
    profile: 'variable',
    description: 'Variable glucose patterns with stress and sleep impact',
    characteristics: [
      'Moderate glucose control (avg 140 mg/dL)',
      'Variable time in range (60%)',
      'Inconsistent sleep (5-7 hours)',
      'Irregular meal timing',
      'Sedentary lifestyle',
      'High glucose variability',
      'Stress-related spikes'
    ],
    avatar: 'BM',
    stats: {
      avgGlucose: 140,
      timeInRange: 60,
      hba1c: 7.2,
      sleepQuality: 65
    }
  },
  {
    id: '33333333-3333-3333-3333-333333333333',
    email: 'carol@demo.glucolens.com',
    fullName: 'Carol Chen',
    age: 28,
    profile: 'active',
    description: 'Active lifestyle with strong exercise impact on glucose',
    characteristics: [
      'Good glucose control (avg 115 mg/dL)',
      'Good time in range (75%)',
      'Regular sleep (7-9 hours)',
      'Athlete diet with proper timing',
      'Very active (exercise 5-6x/week)',
      'Exercise-related glucose dips',
      'Post-workout recovery patterns'
    ],
    avatar: 'CC',
    stats: {
      avgGlucose: 115,
      timeInRange: 75,
      hba1c: 6.3,
      sleepQuality: 80
    }
  }
];

// Demo API configuration
export const DEMO_CONFIG = {
  // Set to true to enable demo mode
  isDemoMode: import.meta.env.VITE_DEMO_MODE === 'true',

  // AWS Lambda API Gateway endpoint (placeholder - will be replaced after deployment)
  apiBaseUrl: import.meta.env.VITE_DEMO_API_URL || 'https://YOUR_API_GATEWAY_ID.execute-api.us-east-1.amazonaws.com/Prod',

  // Demo mode features
  features: {
    readOnly: true,
    noAuthentication: true,
    precomputedInsights: true,
    limitedDataRange: 90 // days
  },

  // Data refresh settings
  cache: {
    ttl: 3600, // 1 hour in seconds
    enabled: true
  }
};

// Get demo user by ID
export function getDemoUserById(userId: string): DemoUser | undefined {
  return DEMO_USERS.find(user => user.id === userId);
}

// Get demo user by profile type
export function getDemoUserByProfile(profile: DemoUser['profile']): DemoUser | undefined {
  return DEMO_USERS.find(user => user.profile === profile);
}

// Check if running in demo mode
export function isDemoMode(): boolean {
  return DEMO_CONFIG.isDemoMode;
}

// Get demo API base URL
export function getDemoApiUrl(): string {
  return DEMO_CONFIG.apiBaseUrl;
}

// Format demo user for display
export function formatDemoUser(user: DemoUser): string {
  return `${user.fullName} (${user.age}y) - ${user.description}`;
}

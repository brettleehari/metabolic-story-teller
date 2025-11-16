import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Index from "./pages/Index";
import DemoIndex from "./pages/DemoIndex";
import DemoDashboard from "./pages/DemoDashboard";
import NotFound from "./pages/NotFound";
import { isDemoMode } from "./config/demo";

const queryClient = new QueryClient();

const App = () => {
  // Redirect to demo if in demo mode
  const shouldRedirectToDemo = isDemoMode();

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            {/* Demo routes */}
            <Route path="/demo" element={<DemoIndex />} />
            <Route path="/demo/dashboard/:userId" element={<DemoDashboard />} />

            {/* Main app routes */}
            <Route
              path="/"
              element={shouldRedirectToDemo ? <Navigate to="/demo" replace /> : <Index />}
            />

            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;

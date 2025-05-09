import AppRoutes from "./routes";
import { Toaster } from "@/components/ui/toaster";

function App() {
  return (
    <div>
      <AppRoutes />
      <Toaster />
    </div>
  );
}

export default App;

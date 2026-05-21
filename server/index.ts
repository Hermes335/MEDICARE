import express from "express";
import cors from "cors";
import authRoutes from "./routes/auth";
import chatRoutes from "./routes/chat";
import pharmacyRoutes from "./routes/pharmacy";
import historyRoutes from "./routes/history";
import savedMedsRoutes from "./routes/saved-meds";

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", service: "MediGuide API" });
});

app.use("/api/auth", authRoutes);
app.use("/api/chat", chatRoutes);
app.use("/api/pharmacy", pharmacyRoutes);
app.use("/api/history", historyRoutes);
app.use("/api/saved-meds", savedMedsRoutes);

app.listen(PORT, () => {
  console.log(`MediGuide API running on http://localhost:${PORT}`);
});

import { Router, Response } from "express";
import db from "../db";
import { authMiddleware, AuthRequest } from "../middleware/auth";

const router = Router();

router.use(authMiddleware);

router.get("/", (req: AuthRequest, res: Response) => {
  const rows = db
    .prepare(
      `SELECT id, symptom, medicine, severity, resolved, created_at as date
       FROM history_entries WHERE user_id = ? ORDER BY created_at DESC`
    )
    .all(req.userId);

  res.json(rows);
});

router.post("/", (req: AuthRequest, res: Response) => {
  const { symptom, medicine, severity } = req.body;

  if (!symptom || !medicine) {
    return res.status(400).json({ error: "symptom and medicine are required" });
  }

  const result = db
    .prepare(
      "INSERT INTO history_entries (user_id, symptom, medicine, severity) VALUES (?, ?, ?, ?)"
    )
    .run(req.userId, symptom, medicine, severity || "mild");

  res.status(201).json({
    id: result.lastInsertRowid,
    symptom,
    medicine,
    severity: severity || "mild",
    resolved: 1,
  });
});

router.delete("/:id", (req: AuthRequest, res: Response) => {
  const { id } = req.params;
  db.prepare("DELETE FROM history_entries WHERE id = ? AND user_id = ?").run(id, req.userId);
  res.status(204).send();
});

export default router;

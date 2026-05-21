import { Router, Response } from "express";
import db from "../db";
import { authMiddleware, AuthRequest } from "../middleware/auth";

const router = Router();

router.use(authMiddleware);

router.get("/", (req: AuthRequest, res: Response) => {
  const rows = db
    .prepare(
      `SELECT id, name, use_text as "use", icon, stock FROM saved_meds WHERE user_id = ? ORDER BY created_at DESC`
    )
    .all(req.userId);

  res.json(rows);
});

router.post("/", (req: AuthRequest, res: Response) => {
  const { name, use: useText, icon, stock } = req.body;

  if (!name) {
    return res.status(400).json({ error: "name is required" });
  }

  const result = db
    .prepare("INSERT INTO saved_meds (user_id, name, use_text, icon, stock) VALUES (?, ?, ?, ?, ?)")
    .run(req.userId, name, useText || "", icon || "\ud83d\udc8a", stock || "");

  res.status(201).json({
    id: result.lastInsertRowid,
    name,
    use: useText || "",
    icon: icon || "\ud83d\udc8a",
    stock: stock || "",
  });
});

router.delete("/:id", (req: AuthRequest, res: Response) => {
  const { id } = req.params;
  db.prepare("DELETE FROM saved_meds WHERE id = ? AND user_id = ?").run(id, req.userId);
  res.status(204).send();
});

export default router;

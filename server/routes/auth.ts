import { Router, Request, Response } from "express";
import bcrypt from "bcryptjs";
import db from "../db";
import { signToken } from "../middleware/auth";

const router = Router();

router.post("/register", (req: Request, res: Response) => {
  const { email, password, name } = req.body;

  if (!email || !password || !name) {
    return res.status(400).json({ error: "Email, password, and name are required" });
  }

  const existing = db.prepare("SELECT id FROM users WHERE email = ?").get(email);
  if (existing) {
    return res.status(409).json({ error: "Email already registered" });
  }

  const hash = bcrypt.hashSync(password, 10);
  const result = db.prepare("INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)").run(email, hash, name);

  const token = signToken(result.lastInsertRowid as number);
  res.json({
    token,
    user: { id: result.lastInsertRowid, email, name },
  });
});

router.post("/login", (req: Request, res: Response) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: "Email and password are required" });
  }

  const user = db.prepare("SELECT id, email, name, password_hash FROM users WHERE email = ?").get(email) as
    | { id: number; email: string; name: string; password_hash: string }
    | undefined;

  if (!user || !bcrypt.compareSync(password, user.password_hash)) {
    return res.status(401).json({ error: "Invalid email or password" });
  }

  const token = signToken(user.id);
  res.json({
    token,
    user: { id: user.id, email: user.email, name: user.name },
  });
});

export default router;

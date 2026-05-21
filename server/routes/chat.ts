import { Router, Request, Response } from "express";

const router = Router();

const PLACEHOLDER_RESPONSES: Record<string, object> = {
  default: {
    name: "Ibuprofen 400mg",
    icon: "\ud83d\udc8a",
    whatItDoes:
      "Ibuprofen is a non-steroidal anti-inflammatory drug (NSAID) that works by blocking prostaglandins\u2014chemicals in your body that cause pain, fever, and inflammation. It's widely used to relieve mild to moderate pain and reduce swelling.",
    effects: [
      "Reduces pain within 30\u201360 minutes",
      "Lowers fever effectively",
      "Reduces inflammation and swelling",
    ],
    sideEffects: [
      "Possible stomach upset if taken on empty stomach",
      "May cause mild dizziness",
      "Avoid with blood thinners or kidney issues",
    ],
    dosage: "1 tablet (400mg)",
    frequency: "Every 6\u20138 hours",
    timing: "With food or milk",
    duration: "3\u20135 days",
    warnings: ["Pregnancy", "Kidney disease", "Stomach ulcers", "Blood thinners"],
    otc: true,
  },
  headache: {
    name: "Paracetamol 500mg",
    icon: "\ud83d\udd35",
    whatItDoes:
      "Paracetamol works centrally to block pain signals in the brain and helps reduce fever. It's one of the safest over-the-counter pain relievers, gentle on the stomach and suitable for most adults.",
    effects: [
      "Relieves headache in 30\u201345 min",
      "Reduces fever effectively",
      "Safe for most adults",
    ],
    sideEffects: [
      "Rare liver risk with high doses",
      "Generally very well tolerated",
      "Avoid alcohol while taking",
    ],
    dosage: "1\u20132 tablets (500mg\u20131g)",
    frequency: "Every 4\u20136 hours",
    timing: "With or without food",
    duration: "Up to 3 days",
    warnings: ["Liver disease", "Heavy alcohol use", "Max 4g/day"],
    otc: true,
  },
  fever: {
    name: "Paracetamol 500mg + Hydration",
    icon: "\ud83c\udf21\ufe0f",
    whatItDoes:
      "For fever management, Paracetamol reduces body temperature by acting on the temperature-regulating center in the brain. Combined with adequate hydration, it helps your immune system fight the underlying cause.",
    effects: [
      "Temperature reduction within 1 hour",
      "Relieves associated body aches",
      "Non-drowsy formula",
    ],
    sideEffects: [
      "Minimal side effects at recommended doses",
      "Drink plenty of fluids",
      "Rest is advised",
    ],
    dosage: "1\u20132 tablets (500mg\u20131g)",
    frequency: "Every 4\u20136 hours",
    timing: "With a full glass of water",
    duration: "Until fever breaks (max 3 days)",
    warnings: ["Liver disease", "Max 4g/day", "See doctor if fever > 39\u00b0C for 48h"],
    otc: true,
  },
  cough: {
    name: "Dextromethorphan Syrup 15mg",
    icon: "\ud83c\udf6f",
    whatItDoes:
      "Dextromethorphan is a cough suppressant that acts on the cough center in the brain to reduce the urge to cough. Best suited for dry, irritating coughs.",
    effects: [
      "Suppresses dry cough for 4\u20136 hours",
      "Helps you sleep more comfortably",
      "Non-sedating at standard doses",
    ],
    sideEffects: [
      "Mild drowsiness possible",
      "Do not use for productive (wet) cough",
      "Avoid driving if drowsy",
    ],
    dosage: "10ml (1 full spoon)",
    frequency: "Every 6\u20138 hours",
    timing: "After meals",
    duration: "Up to 7 days",
    warnings: ["MAOI medications", "Productive cough", "Under 12 years"],
    otc: true,
  },
  stomach: {
    name: "Buscopan (Hyoscine) 10mg",
    icon: "\ud83d\udfe2",
    whatItDoes:
      "Hyoscine butylbromide relieves intestinal spasms and cramps by relaxing the smooth muscles of the gut. It works locally in the digestive tract for fast, targeted relief.",
    effects: [
      "Relieves cramps within 15\u201330 min",
      "Reduces bloating",
      "Targeted gut relief",
    ],
    sideEffects: [
      "Dry mouth possible",
      "Slight blurred vision temporarily",
      "Do not drive if vision affected",
    ],
    dosage: "1\u20132 tablets (10\u201320mg)",
    frequency: "Every 6\u20138 hours",
    timing: "Before or with meals",
    duration: "3\u20135 days",
    warnings: ["Glaucoma", "Enlarged prostate", "Pregnancy"],
    otc: true,
  },
  allerg: {
    name: "Cetirizine 10mg",
    icon: "\ud83c\udf3f",
    whatItDoes:
      "Cetirizine is a second-generation antihistamine that blocks H1 receptors, preventing histamine from causing allergy symptoms. Provides 24-hour relief with minimal drowsiness.",
    effects: [
      "Controls sneezing and runny nose",
      "Relieves itchy, watery eyes",
      "24-hour protection per dose",
    ],
    sideEffects: [
      "Mild drowsiness in some people",
      "Dry mouth occasionally",
      "Avoid alcohol",
    ],
    dosage: "1 tablet (10mg)",
    frequency: "Once daily",
    timing: "Evening (may cause mild drowsiness)",
    duration: "As needed or daily during allergy season",
    warnings: ["Kidney impairment", "Pregnancy (consult doctor)", "Avoid with alcohol"],
    otc: true,
  },
};

router.post("/", (req: Request, res: Response) => {
  const { message } = req.body;

  if (!message || typeof message !== "string") {
    return res.status(400).json({ error: "Message is required" });
  }

  const lower = message.toLowerCase();
  const key = Object.keys(PLACEHOLDER_RESPONSES).find((k) => k !== "default" && lower.includes(k));
  const medicine = PLACEHOLDER_RESPONSES[key ?? "default"];

  // Simulate network delay (placeholder — real model will replace this)
  setTimeout(() => {
    res.json({
      ack: `I understand you're experiencing **${message.toLowerCase()}**. Based on your symptoms, I've reviewed our pharmaceutical database and have a recommendation that may help provide relief. Please review the information below carefully.`,
      medicine,
    });
  }, 800);
});

export default router;

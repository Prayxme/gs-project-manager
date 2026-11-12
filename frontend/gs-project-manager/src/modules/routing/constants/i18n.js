export const I18N = {
  es: {
    title: "Routing (RTS)",
    subtitle:
      "Sube los PDFs de Pick Tickets: cada PO se concilia con el portal de Wiesner, se estiman sus pallets (con margen) y se agrupan en RTS por dirección SHIP TO y Cancel Date. Haz clic en cualquier valor para copiarlo.",
    upload: "📄 Subir PDFs de Pick Tickets",
    urgentButton: "⚡ Urgentes del monitor",
    working: "Leyendo PDFs, consultando el portal y estimando pallets...",
    workingUrgent: "Consultando el portal y estimando las órdenes urgentes...",
    empty: "Sube PDFs de Pick Tickets o pulsa «Urgentes del monitor» para calcular las órdenes que vencen hoy o en los próximos días.",
    urgentIntro:
      "{n} órdenes del portal sin routing con fecha límite vencida, hoy o en los próximos {d} días. Se calcularon con los Pick Tickets ya recibidos; faltan {m}.",
    routedTitle: "Ya enrutadas en Wiesner",
    routedHint: "El portal ya muestra su número de confirmación: no se estiman de nuevo.",
    cfrm: "Cfrm",
    appt: "Cita",
    missingTitle: "Órdenes urgentes sin Pick Ticket",
    missingHint: "Están en el portal y vencen pronto, pero no se ha recibido su PDF: súbelo para poder estimarlas.",
    files: "Archivos",
    portalOk: "Portal de Wiesner consultado: {n} órdenes abiertas.",
    portalDown:
      "No se pudo consultar el portal de Wiesner ({e}). Los datos salen solo del PDF y NO están verificados: no enrutes sin revisar PO, PikTik y cartones.",
    summary: {
      pos: "POs", rts: "RTS", pallets: "Pallets a enrutar", already_routed: "Ya enrutadas",
      excluded: "Con problemas",
    },
    rts: "RTS {n}",
    cancel: "Cancel",
    deadline: "Fecha límite",
    limit: "{p} / {l} pallets",
    overLimit: "Supera el límite de {l} pallets: hay que dividir esta PO",
    unverified: "Sin verificar con el portal",
    totals: "Total RTS",
    cols: {
      po: "PO", piktik: "PikTik", cust: "Cust#", units: "Unidades", cartons: "Cartones",
      weight: "LB", cft: "CFT", pallets: "Pallets", estimated: "estimado {n}",
    },
    weightAdjusted: "mínimo 3100 lb (real {w})",
    days: {
      overdue: "Vencido hace {n} día(s)", today: "Último día: hoy", soon: "Faltan {n} día(s)", later: "Faltan {n} días",
    },
    excludedTitle: "POs que no se pueden enrutar",
    excludedHint: "El portal de Wiesner es la verdad: revisa estas POs antes de enrutarlas.",
    status: {
      OK: "Verificada", UNVERIFIED: "Sin verificar", MISMATCH: "No coincide con el portal",
      NOT_IN_PORTAL: "No está en el portal", ALREADY_ROUTED: "Ya tiene Cfrm", NO_ITEMS: "PDF sin líneas",
    },
    warnings: "Avisos de lectura ({n})",
    rules:
      "Reglas: margen sobre lo estimado (1→2, 2→3, 3–10 +2, 11–20 +3, >20 +15 %) · LB = cajas + 45 lb por pallet · CFT = 90 × pallets (BURL/MODE) o 130 × pallets · máx. 28 pallets por RTS (26 ROSS/DDSD) · ROSS/DDSD mínimo 3100 lb por RTS.",
  },
  en: {
    title: "Routing (RTS)",
    subtitle:
      "Upload Pick Ticket PDFs: each PO is reconciled with the Wiesner portal, its pallets are estimated (with margin) and grouped into RTS by SHIP TO address and Cancel Date. Click any value to copy it.",
    upload: "📄 Upload Pick Ticket PDFs",
    urgentButton: "⚡ Urgent from monitor",
    working: "Reading PDFs, checking the portal and estimating pallets...",
    workingUrgent: "Checking the portal and estimating urgent orders...",
    empty: "Upload Pick Ticket PDFs or press “Urgent from monitor” to calculate the orders due today or in the next few days.",
    urgentIntro:
      "{n} portal orders without routing whose deadline is past, today or within the next {d} days. Calculated with the Pick Tickets already received; {m} missing.",
    routedTitle: "Already routed in Wiesner",
    routedHint: "The portal already shows their confirmation number: they are not estimated again.",
    cfrm: "Cfrm",
    appt: "Appt",
    missingTitle: "Urgent orders without Pick Ticket",
    missingHint: "They are in the portal and due soon, but their PDF has not been received: upload it to estimate them.",
    files: "Files",
    portalOk: "Wiesner portal checked: {n} open orders.",
    portalDown:
      "The Wiesner portal could not be reached ({e}). Data comes only from the PDF and is NOT verified: do not route without checking PO, PikTik and cartons.",
    summary: {
      pos: "POs", rts: "RTS", pallets: "Pallets to route", already_routed: "Already routed",
      excluded: "With problems",
    },
    rts: "RTS {n}",
    cancel: "Cancel",
    deadline: "Deadline",
    limit: "{p} / {l} pallets",
    overLimit: "Exceeds the {l}-pallet limit: this PO must be split",
    unverified: "Not verified with the portal",
    totals: "RTS total",
    cols: {
      po: "PO", piktik: "PikTik", cust: "Cust#", units: "Units", cartons: "Cartons",
      weight: "LB", cft: "CFT", pallets: "Pallets", estimated: "estimated {n}",
    },
    weightAdjusted: "3100 lb minimum (actual {w})",
    days: {
      overdue: "Overdue by {n} day(s)", today: "Last day: today", soon: "{n} day(s) left", later: "{n} days left",
    },
    excludedTitle: "POs that cannot be routed",
    excludedHint: "The Wiesner portal is the source of truth: review these POs before routing them.",
    status: {
      OK: "Verified", UNVERIFIED: "Not verified", MISMATCH: "Does not match the portal",
      NOT_IN_PORTAL: "Not in the portal", ALREADY_ROUTED: "Already has Cfrm", NO_ITEMS: "PDF without lines",
    },
    warnings: "Reading warnings ({n})",
    rules:
      "Rules: margin over the estimate (1→2, 2→3, 3–10 +2, 11–20 +3, >20 +15%) · LB = cartons + 45 lb per pallet · CFT = 90 × pallets (BURL/MODE) or 130 × pallets · max 28 pallets per RTS (26 ROSS/DDSD) · ROSS/DDSD minimum 3100 lb per RTS.",
  },
};

// "PICK-TICKETS - 00WPI - Whse:PM - Cust:MARS125 - 2026-11-11" -> "MARS125" ("all" si trae varios clientes)
export const clienteDelAsunto = (asunto) => (asunto || "").match(/Cust:\s*([^\s-]+)/i)?.[1] || "";

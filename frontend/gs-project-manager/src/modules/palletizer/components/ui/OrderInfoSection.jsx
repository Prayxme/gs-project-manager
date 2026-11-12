// Datos generales de la orden (PO y PikTik) en el formulario de carga.
export default function OrderInfoSection({ orderInfo, setOrderInfo, t }) {
  return (
    <section className="space-y-2">
      <h3 className="text-xs font-extrabold uppercase tracking-widest text-brand">{t.orderInfoTitle}</h3>
      <div className="grid grid-cols-2 gap-2">
        {[["po", t.poNumber], ["piktik", t.pikTik]].map(([campo, etiqueta]) => (
          <label key={campo}>
            <span className="label">{etiqueta}</span>
            <input
              type="text"
              value={orderInfo[campo]}
              onChange={(e) => setOrderInfo({ ...orderInfo, [campo]: e.target.value })}
              className="input font-mono py-1.5"
            />
          </label>
        ))}
      </div>
    </section>
  );
}

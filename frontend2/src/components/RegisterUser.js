import React, { useState } from "react";

function RegisterUser() {
  const [form, setForm] = useState({ opCode: "", name: "", dni: "", descriptor: "" });

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleRegister = async () => {
    const res = await fetch("http://localhost:8000/users/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });
    const data = await res.json();
    alert(data.msg || "Usuario registrado");
  };

  return (
    <div className="container">
      <h2>Registro de Usuario</h2>
      <input name="opCode" placeholder="opCode" onChange={handleChange} />
      <input name="name" placeholder="Nombre" onChange={handleChange} />
      <input name="dni" placeholder="DNI" onChange={handleChange} />
      <input name="descriptor" placeholder="Descriptor" onChange={handleChange} />
      <button onClick={handleRegister}>Registrar</button>
    </div>
  );
}

export default RegisterUser;
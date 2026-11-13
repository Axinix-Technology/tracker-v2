import React from "react";
import { Navigate } from "react-router-dom";

export default function ContributionsIndex() {
  return <Navigate to="/contributions/dashboard" replace />;
}


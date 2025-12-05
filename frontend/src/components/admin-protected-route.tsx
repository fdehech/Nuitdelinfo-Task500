import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import AdminDashboard from "@/components/admin-dashboard"

export default function AdminProtectedRoute() {
    const navigate = useNavigate()
    const [isAuthorized, setIsAuthorized] = useState(false)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        // Check if user is logged in and is admin
        const loggedIn = localStorage.getItem("userLoggedIn") === "true"
        const userType = localStorage.getItem("userType")

        if (!loggedIn) {
            navigate("/login")
        } else if (userType !== "admin") {
            navigate("/")
        } else {
            setIsAuthorized(true)
        }

        setIsLoading(false)
    }, [navigate])

    if (isLoading) return null

    return isAuthorized ? <AdminDashboard /> : null
}

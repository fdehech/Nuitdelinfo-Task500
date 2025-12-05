import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import DocumentAnalyzer from "@/components/document-analyzer"

export default function ProtectedRoute() {
    const navigate = useNavigate()
    const [isLoggedIn, setIsLoggedIn] = useState(false)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        // Check if user is logged in
        const loggedIn = localStorage.getItem("userLoggedIn") === "true"
        setIsLoggedIn(loggedIn)
        setIsLoading(false)

        if (!loggedIn) {
            navigate("/login")
        }
    }, [navigate])

    if (isLoading) return null

    return isLoggedIn ? <DocumentAnalyzer /> : null
}

import { useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { Mail, Lock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { api } from "@/lib/api"

export default function LoginPage() {
    const navigate = useNavigate()
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [authMethod, setAuthMethod] = useState<"email" | "sso">("email")
    const [userType, setUserType] = useState<"user" | "admin">("user")
    const [isLoading, setIsLoading] = useState(false)

    const handleEmailLogin = async (e: FormEvent) => {
        e.preventDefault()
        setIsLoading(true)

        try {
            // 1. Login to get token (using fetch directly for x-www-form-urlencoded)
            const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
            const response = await fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ username: email, password: password })
            });

            if (!response.ok) throw new Error("Login failed");

            const tokenData = await response.json();
            localStorage.setItem("accessToken", tokenData.access_token);

            // 2. Get user details
            const user = await api.get<{ is_superuser: boolean, email: string, full_name: string }>("/users/me", {
                token: tokenData.access_token
            });

            localStorage.setItem("userLoggedIn", "true")
            localStorage.setItem("userEmail", user.email)
            localStorage.setItem("userType", user.is_superuser ? "admin" : "user")

            navigate(user.is_superuser ? "/admin" : "/")
        } catch (error) {
            console.error("Login error:", error)
            alert("Login failed. Please check your credentials.")
        } finally {
            setIsLoading(false)
        }
    }

    const handleSSOLogin = async (provider: "google" | "github") => {
        setIsLoading(true)

        // Mock SSO flow
        await new Promise((resolve) => setTimeout(resolve, 2000))

        localStorage.setItem("userLoggedIn", "true")
        localStorage.setItem("userProvider", provider)
        localStorage.setItem("userType", userType)
        setIsLoading(false)
        navigate(userType === "admin" ? "/admin" : "/")
    }

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-6 grid-bg scanlines">
            <div className="w-full max-w-md space-y-8">
                {/* Header */}
                <div className="text-center space-y-4">
                    <div className="flex items-center justify-center gap-2">
                        <div className="text-4xl font-mono pulse-accent">▓▒░</div>
                        <h1 className="text-4xl font-bold text-accent font-mono">DOC.ROASTER</h1>
                    </div>
                    <p className="text-muted-foreground text-sm font-mono">&gt; ACCESS GRANTED... maybe</p>
                </div>

                {/* Login Card */}
                <Card className="p-8 bg-card border-2 border-accent/50 card-glow">
                    <div className="space-y-6">
                        {/* User Type Selection */}
                        <div className="flex gap-2 border-b border-accent/30 mb-6">
                            <button
                                onClick={() => setUserType("user")}
                                className={`flex-1 pb-3 text-center text-sm font-mono font-semibold transition-colors ${userType === "user"
                                    ? "text-accent border-b-2 border-accent"
                                    : "text-muted-foreground hover:text-accent/70"
                                    }`}
                            >
                                USER LOGIN
                            </button>
                            <button
                                onClick={() => setUserType("admin")}
                                className={`flex-1 pb-3 text-center text-sm font-mono font-semibold transition-colors ${userType === "admin"
                                    ? "text-accent border-b-2 border-accent"
                                    : "text-muted-foreground hover:text-accent/70"
                                    }`}
                            >
                                ADMIN LOGIN
                            </button>
                        </div>

                        {/* Tab Selection for Auth Method */}
                        <div className="flex gap-2 border-b border-accent/30 mb-6">
                            <button
                                onClick={() => setAuthMethod("email")}
                                className={`flex-1 pb-3 text-center text-sm font-mono font-semibold transition-colors ${authMethod === "email"
                                    ? "text-accent border-b-2 border-accent"
                                    : "text-muted-foreground hover:text-accent/70"
                                    }`}
                            >
                                EMAIL/PASSWORD
                            </button>
                            <button
                                onClick={() => setAuthMethod("sso")}
                                className={`flex-1 pb-3 text-center text-sm font-mono font-semibold transition-colors ${authMethod === "sso"
                                    ? "text-accent border-b-2 border-accent"
                                    : "text-muted-foreground hover:text-accent/70"
                                    }`}
                            >
                                SSO
                            </button>
                        </div>

                        {/* Email/Password Form */}
                        {authMethod === "email" && (
                            <form onSubmit={handleEmailLogin} className="space-y-4">
                                <div>
                                    <label className="block text-xs font-medium text-accent mb-2 font-mono">&gt; EMAIL:</label>
                                    <div className="relative">
                                        <Mail size={18} className="absolute left-3 top-3 text-accent/60" />
                                        <input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="your@email.com"
                                            required
                                            className="w-full pl-10 pr-4 py-3 rounded-none border border-border bg-muted text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-accent font-mono text-sm"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-medium text-accent mb-2 font-mono">&gt; PASSWORD:</label>
                                    <div className="relative">
                                        <Lock size={18} className="absolute left-3 top-3 text-accent/60" />
                                        <input
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="••••••••"
                                            required
                                            className="w-full pl-10 pr-4 py-3 rounded-none border border-border bg-muted text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-accent font-mono text-sm"
                                        />
                                    </div>
                                </div>

                                <Button
                                    type="submit"
                                    disabled={isLoading || !email || !password}
                                    className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-semibold py-3 h-auto font-mono rounded-none"
                                >
                                    {isLoading ? "[AUTHENTICATING...]" : "[LOGIN]"}
                                </Button>

                                <div className="text-center text-xs text-muted-foreground font-mono">
                                    <p className="mt-4">password hint: it's probably "password123"</p>
                                </div>
                            </form>
                        )}

                        {/* SSO Options */}
                        {authMethod === "sso" && (
                            <div className="space-y-3">
                                <p className="text-xs text-muted-foreground font-mono mb-4">&gt; CHOOSE YOUR PROVIDER:</p>

                                <Button
                                    onClick={() => handleSSOLogin("google")}
                                    disabled={isLoading}
                                    className="w-full bg-accent/20 hover:bg-accent/30 text-accent border-2 border-accent font-semibold py-3 h-auto font-mono rounded-none"
                                    variant="outline"
                                >
                                    {isLoading ? "[CONNECTING...]" : "[SIGN IN WITH GOOGLE]"}
                                </Button>

                                <Button
                                    onClick={() => handleSSOLogin("github")}
                                    disabled={isLoading}
                                    className="w-full bg-accent/20 hover:bg-accent/30 text-accent border-2 border-accent font-semibold py-3 h-auto font-mono rounded-none"
                                    variant="outline"
                                >
                                    {isLoading ? "[CONNECTING...]" : "[SIGN IN WITH GITHUB]"}
                                </Button>

                                <div className="text-center text-xs text-muted-foreground font-mono">
                                    <p className="mt-4">▓ neither will actually work right now, but click anyway ▓</p>
                                </div>
                            </div>
                        )}

                        {/* Divider */}
                        <div className="flex items-center gap-3 text-muted-foreground font-mono text-xs">
                            <div className="flex-1 border-t border-border"></div>
                            <span>&gt; OR &lt;</span>
                            <div className="flex-1 border-t border-border"></div>
                        </div>

                        {/* Toggle Button */}
                        <div className="text-center">
                            {authMethod === "email" ? (
                                <p className="text-xs text-muted-foreground font-mono">
                                    prefer{" "}
                                    <button onClick={() => setAuthMethod("sso")} className="text-accent hover:underline font-semibold">
                                        SSO?
                                    </button>
                                </p>
                            ) : (
                                <p className="text-xs text-muted-foreground font-mono">
                                    prefer{" "}
                                    <button onClick={() => setAuthMethod("email")} className="text-accent hover:underline font-semibold">
                                        email?
                                    </button>
                                </p>
                            )}
                        </div>
                    </div>
                </Card>

                {/* Footer Message */}
                <div className="text-center space-y-2">
                    <p className="text-xs text-muted-foreground font-mono">&gt; you ARE the documents now</p>
                    <p className="text-xs text-accent/60 font-mono">v0.ROASTER // SYSTEM READY</p>
                </div>

                {/* Quick Access Link */}
                <div className="text-center">
                    <button
                        onClick={() => navigate("/")}
                        className="text-sm text-accent hover:underline font-mono font-semibold"
                    >
                        skip to dashboard →
                    </button>
                </div>
            </div>
        </div>
    )
}

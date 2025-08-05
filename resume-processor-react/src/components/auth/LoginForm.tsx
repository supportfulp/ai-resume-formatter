import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { authAPI } from '../../services/api'
import { useAuthStore } from '../../store/useAuthStore'
import { toast } from 'sonner'

interface LoginFormData {
  username: string
  password: string
  email?: string
}

const LoginForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const { login, setDemoMode } = useAuthStore()

  const loginForm = useForm<LoginFormData>()
  const registerForm = useForm<LoginFormData>()

  const onLogin = async (data: LoginFormData) => {
    setIsLoading(true)
    try {
      if (data.username === 'demo' && data.password === 'demo123') {
        // Demo mode
        login({
          id: 1,
          username: 'demo',
          email: 'demo@example.com',
        })
        setDemoMode(true)
        toast.success('Logged in as demo user')
      } else {
        // Real login
        const response = await authAPI.login(data.username, data.password)
        if (response.success && response.data) {
          login(response.data)
          toast.success('Logged in successfully')
        } else {
          toast.error(response.error || 'Login failed')
        }
      }
    } catch (error) {
      toast.error('Login failed. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }

  const onRegister = async (data: LoginFormData) => {
    setIsLoading(true)
    try {
      const response = await authAPI.register(data.username, data.password, data.email)
      if (response.success && response.data) {
        login(response.data)
        toast.success('Account created successfully')
      } else {
        toast.error(response.error || 'Registration failed')
      }
    } catch (error) {
      toast.error('Registration failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">
            🔐 Resume Processor
          </h1>
          <p className="text-gray-600">
            AI-Powered Resume Analysis & Restructuring
          </p>
        </div>

        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">🔐 Login</TabsTrigger>
            <TabsTrigger value="register">📝 Register</TabsTrigger>
          </TabsList>

          <TabsContent value="login">
            <Card>
              <CardHeader>
                <CardTitle>Welcome Back!</CardTitle>
                <CardDescription>Sign in to your account to continue</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={loginForm.handleSubmit(onLogin)} className="space-y-4">
                  <div>
                    <Input
                      placeholder="Enter your username"
                      {...loginForm.register('username', { required: true })}
                    />
                    <p className="text-sm text-gray-500 mt-1">Username</p>
                  </div>
                  <div>
                    <Input
                      type="password"
                      placeholder="Enter your password"
                      {...loginForm.register('password', { required: true })}
                    />
                    <p className="text-sm text-gray-500 mt-1">Password</p>
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" disabled={isLoading} className="flex-1">
                      {isLoading ? 'Signing in...' : '🔐 Sign In'}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => onLogin({ username: 'demo', password: 'demo123' })}
                      disabled={isLoading}
                    >
                      🧪 Demo
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="register">
            <Card>
              <CardHeader>
                <CardTitle>Create Account</CardTitle>
                <CardDescription>Sign up for a new account</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={registerForm.handleSubmit(onRegister)} className="space-y-4">
                  <div>
                    <Input
                      placeholder="Enter your username"
                      {...registerForm.register('username', { required: true })}
                    />
                    <p className="text-sm text-gray-500 mt-1">Username</p>
                  </div>
                  <div>
                    <Input
                      type="email"
                      placeholder="Enter your email (optional)"
                      {...registerForm.register('email')}
                    />
                    <p className="text-sm text-gray-500 mt-1">Email (optional)</p>
                  </div>
                  <div>
                    <Input
                      type="password"
                      placeholder="Enter your password"
                      {...registerForm.register('password', { required: true })}
                    />
                    <p className="text-sm text-gray-500 mt-1">Password</p>
                  </div>
                  <Button type="submit" disabled={isLoading} className="w-full">
                    {isLoading ? 'Creating Account...' : '📝 Create Account'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default LoginForm
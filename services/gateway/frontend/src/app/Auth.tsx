import { z } from "zod"
import { useForm } from "@mantine/form"
import { zod4Resolver } from "mantine-form-zod-resolver"
import { useState, useEffect } from "react"
import { fetch } from "@/lib/openapi/index"
import { useSearchParams, useNavigate } from "react-router-dom"
import { TextInput, Button, PasswordInput } from "@mantine/core"

const formSchema = z.object({
  username: z
    .string()
    .min(6, "Username must be at least 6 characters")
    .max(18, "Username must be at most 18 characters")
    .regex(
      /^[\w.@+-]+$/,
      "Username may contain only letters, numbers, and @/./+/-/_ characters"
    ),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(64, "Password must be at most 64 characters"),
})

export default function Auth() {
  const [search_params, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const [isLogin, setIsLogin] = useState(search_params.get("mode") === "login")
  useEffect(() => {
    const isLoggedIn = async () => {
      try {
        const { data, response, error: err } = await fetch.GET("/api/me")
        if (data) {
          navigate("/")
        } else if (response.status !== 401) {
          console.error(err) // TODO better error handling
          navigate("/error")
        }
      } catch (err) {
        console.error(err) // TODO better error handling
        navigate("/error")
      }
    }
    isLoggedIn()

    if (isLogin) {
      setSearchParams({ mode: "login" })
    } else {
      setSearchParams({ mode: "signup" })
    }
  }, [isLogin, setSearchParams])

  const form = useForm({
    mode: "uncontrolled",
    initialValues: {
      username: "",
      password: "",
    },
    validate: zod4Resolver(formSchema),
  })

  return (
    <main className="w-screen h-screen flex justify-center items-center">
      <form
        onSubmit={form.onSubmit(async (form_values) => {
          const { username, password } = form_values

          try {
            if (isLogin) {
              const { error: err, response } = await fetch.POST("/api/login", {
                body: {
                  username,
                  password,
                },
              })

              if (err) {
                if (response.status === 401) {
                  form.setFieldValue("password", "")
                  form.setErrors({
                    username: " ",
                    password:
                      "Invalid credentials, failed to login. Try again.",
                  })

                  return
                } else {
                  console.error(err) // TODO better error handling
                  navigate("/error")
                }
              }
            } else {
              const { error: err, response } = await fetch.POST("/api/signup", {
                body: {
                  username,
                  password,
                },
              })

              if (err) {
                if (
                  response.status === 400 &&
                  err.detail.includes(
                    "A user with that username already exists."
                  )
                ) {
                  form.setFieldValue("password", "")
                  form.setErrors({
                    username: " ",
                    password:
                      "A user with that username already exists. Login instead.",
                  })

                  return
                } else {
                  console.error(err) // TODO better error handling
                  navigate("/error")
                }
              }
            }

            navigate("/")
          } catch (err) {
            console.error(err) // TODO better error handling
            navigate("/error")
          }
        })}
        className="flex flex-col w-1/3 border p-4"
        style={{ borderColor: "var(--mantine-color-gray-4)" }}
      >
        <TextInput
          id="input_username"
          key={form.key("username")}
          label="Username"
          placeholder="Your username"
          mb="md"
          {...form.getInputProps("username")}
        />
        <PasswordInput
          id="input_password"
          key={form.key("password")}
          label="Password"
          placeholder="********"
          mb="lg"
          {...form.getInputProps("password")}
        />
        <Button id="button_submit" type="submit" mb="sm">
          {isLogin ? "Log In" : "Sign Up"}
        </Button>
        <div className="mt-2 text-sm text-right">
          <span className="mr-1">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
          </span>
          <Button
            id="button_toggle_mode"
            type="button"
            onClick={() => setIsLogin((prev) => !prev)}
            variant="light"
            size="xs"
            m="0"
            px="xs"
          >
            {isLogin ? "Sign Up" : "Log In"}
          </Button>
        </div>
      </form>
    </main>
  )
}

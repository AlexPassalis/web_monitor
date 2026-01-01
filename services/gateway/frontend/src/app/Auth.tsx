import { useState, useRef, useEffect } from "react"
import { fetch } from "@/lib/openapi/index"
import { useSearchParams } from "react-router-dom"

export default function Auth() {
  const [search_params, setSearchParams] = useSearchParams()
  const [isLogin, setIsLogin] = useState(search_params.get("mode") === "login")
  useEffect(() => {
    if (isLogin) {
      setSearchParams({ mode: "login" })
    } else {
      setSearchParams({ mode: "signup" })
    }
  }, [isLogin, setSearchParams])

  const input_username_ref = useRef<HTMLInputElement>(null)
  const input_password_ref = useRef<HTMLInputElement>(null)

  return (
    <main className="w-screen h-screen flex justify-center items-center">
      <form
        onSubmit={async (e) => {
          e.preventDefault()

          if (!input_username_ref.current || !input_password_ref.current) {
            // TODO better data handling here
            return
          }

          try {
            if (isLogin) {
              const { error: err } = await fetch.POST("/api/login", {
                body: {
                  username: input_username_ref.current.value,
                  password: input_password_ref.current.value,
                },
              })

              if (err) {
                // TODO better error handling
                console.error(err)
                return
              }
            } else {
              const { error: err } = await fetch.POST("/api/signup", {
                body: {
                  username: input_username_ref.current.value,
                  password: input_password_ref.current.value,
                },
              })

              if (err) {
                // TODO better error handling
                console.error(err)
                return
              }
            }

            window.location.href = "/"
          } catch (err) {
            console.error(err) // TODO better error handling
          }
        }}
        className="flex flex-col w-1/3 border border-black p-4"
      >
        <label htmlFor="input_username">Username</label>
        <input
          id="input_username"
          ref={input_username_ref}
          type="text"
          className="border border-black rounded-md p-1 mb-1"
        />
        <label htmlFor="input_password">Password</label>
        <input
          id="input_password"
          ref={input_password_ref}
          type="password"
          className="border border-black rounded-md p-1"
        />
        <button
          id="button_submit"
          type="submit"
          className="self-center w-auto p-1 border border-black mt-4 text-lg hover:cursor-pointer"
        >
          {isLogin ? "Log In" : "Sign Up"}
        </button>
        <div className="mt-2 text-sm text-right">
          <span className="mr-1">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
          </span>
          <button
            id="button_toggle_mode"
            onClick={() => setIsLogin((prev) => !prev)}
            type="button"
            className="border border-black rounded-md p-0.5 hover:cursor-pointer"
          >
            {isLogin ? "Sign Up" : "Log In"}
          </button>
        </div>
      </form>
    </main>
  )
}

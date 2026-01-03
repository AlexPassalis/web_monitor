import { Link } from "react-router-dom"

export default function Error() {
  return (
    <main className="w-screen h-screen flex flex-col justify-center items-center">
      <h1 className="text-6xl">Error - 500</h1>
      <h1 className="text-3xl mt-6 mb-10">
        The server encountered an error and could not complete your request.
      </h1>
      <Link
        to="/"
        className="border border-black p-1 text-xl hover:cursor-pointer hover:bg-blue-600 hover:text-white"
      >
        Take me back to the home page
      </Link>
    </main>
  )
}

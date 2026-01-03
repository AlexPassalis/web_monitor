import type { components } from "@/lib/openapi/schema"

import { useRef, useState, useEffect } from "react"
import { fetch } from "@/lib/openapi/index"
import { useForm } from "@mantine/form"
import { zod4Resolver } from "mantine-form-zod-resolver"
import { z } from "zod"
import {
  Table,
  Select,
  TextInput,
  Button,
  Modal,
  Text,
  Flex,
} from "@mantine/core"
import { useDisclosure } from "@mantine/hooks"
import { Carousel } from "@mantine/carousel"
import Image from "@/components/Image"
import { MdDelete, MdAdd } from "react-icons/md"
import { notifications } from "@mantine/notifications"
import { useNavigate } from "react-router-dom"

const formSchema = z.object({
  interval: z.enum(["minute", "hour", "day"], {
    error: "Choose an interval between minute, hour or day",
  }),
  url: z.url({ error: "Invalid URL" }),
})

export default function Home() {
  const csrf = useRef("")
  const [webpages, setWebpages] = useState<
    components["schemas"]["WebpageDetail"][]
  >([])
  console.info(webpages)

  const modal_data = useRef<
    | {
        type: "screenshots" | "delete";
        webpage: components["schemas"]["WebpageDetail"];
      }
    | undefined
  >(undefined)
  const [is_modal_open, { open: open_modal, close: close_modal }] =
    useDisclosure(false)

  const navigate = useNavigate()
  useEffect(() => {
    const fetchData = async () => {
      try {
        const resolved = await Promise.all([
          fetch.GET("/api/webpage"),
          fetch.GET("/api/csrf"),
        ])

        const [
          { error: err_webpage, response: resp_webpage, data: data_webpage },
          { error: err_csrf, data: data_csrf },
        ] = resolved

        if (err_webpage) {
          console.error(err_webpage) // TODO better error handling
          if (resp_webpage.status === 401) {
            navigate("/auth?mode=login")
          }
        } else if (err_csrf) {
          console.error(err_csrf) // TODO better error handling
        } else {
          csrf.current = data_csrf.csrfToken
          setWebpages(data_webpage)
        }
      } catch (err) {
        console.error(err) // TODO better error handling
      }
    }

    fetchData()
  }, [])

  const form = useForm({
    mode: "uncontrolled",
    initialValues: {
      interval: "minute",
      url: "",
    } satisfies z.infer<typeof formSchema>,
    validate: zod4Resolver(formSchema),
  })

  return (
    <>
      <Modal
        opened={is_modal_open}
        onClose={() => {
          close_modal()
          modal_data.current = undefined
        }}
        title={
          modal_data.current && (
            <Text size="xl">
              {modal_data.current.type === "screenshots" ? (
                <>
                  Screenshots of{" "}
                  <Text span c="blue">
                    {modal_data.current.webpage.url}
                  </Text>
                </>
              ) : (
                "Webpage removal confirmation"
              )}
            </Text>
          )
        }
        centered
        size={
          modal_data.current &&
          (modal_data.current.type === "screenshots"
            ? "100%"
            : modal_data.current.type === "delete"
            ? "md"
            : undefined)
        }
        overlayProps={{
          backgroundOpacity: 0.75,
          blur: 2,
        }}
        transitionProps={{ transition: "scale" }}
        styles={{ title: { width: "100%", textAlign: "center" } }}
      >
        {modal_data.current && (
          <>
            {modal_data.current.type === "screenshots" && (
              <Carousel
                withIndicators
                withControls
                controlSize={40}
                controlsOffset="lg"
                height="70vh"
                slideGap="md"
                slideSize="100%"
                emblaOptions={{ loop: false }}
                styles={{
                  control: {
                    backgroundColor: "white",
                    color: "black",
                  },
                }}
              >
                {modal_data.current.webpage.screenshots.map((timestamp) => {
                  const id = modal_data.current?.webpage.id
                  const url = modal_data.current?.webpage.url
                  const path = `webpage/${id}/${timestamp}.png`
                  return (
                    <Carousel.Slide key={path}>
                      <Flex direction="column" align="center">
                        <Image
                          src={path}
                          alt={`Webpagescreenshot of ${url} at ${timestamp}`}
                          className="w-full max-h-[62vh] object-contain"
                        />
                        <Text ta="center" size="lg" mt="md">
                          {timestamp}
                        </Text>
                      </Flex>
                    </Carousel.Slide>
                  )
                })}
              </Carousel>
            )}
            {modal_data.current.type === "delete" && (
              <>
                <Text>
                  Are you sure you want to stop monitoring the "
                  {modal_data.current?.webpage.url}" webpage and delete all
                  related information?
                </Text>
                <Flex justify="center" gap="md" mt="md">
                  <Button type="button" onClick={() => close_modal()}>
                    Don't delete
                  </Button>
                  <Button
                    type="button"
                    onClick={async () => {
                      try {
                        const { error: err, data } = await fetch.DELETE(
                          "/api/webpage",
                          {
                            headers: {
                              "X-CSRFToken": csrf.current,
                            },
                            body: {
                              id: modal_data.current!.webpage.id,
                            },
                          }
                        )

                        if (err) {
                          console.error(err) // TODO better error handling
                        } else {
                          setWebpages((prev) =>
                            prev.filter((webpage) => webpage.id !== data.id)
                          )
                          notifications.show({
                            message: `Webpage "${data.url}" has successfully been removed from being monitored.`,
                            withCloseButton: false,
                            autoClose: 3000,
                            color: "green",
                          })
                        }
                      } catch (err) {
                        console.error(err) // TODO better error handling
                      } finally {
                        close_modal()
                      }
                    }}
                    color="red"
                  >
                    Delete
                  </Button>
                </Flex>
              </>
            )}
          </>
        )}
      </Modal>

      <main className="p-10">
        <Table highlightOnHover withTableBorder>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>URL</Table.Th>
              <Table.Th>Interval</Table.Th>
              <Table.Th ta="center">Updates</Table.Th>
              <Table.Th ta="center">Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {webpages.map(({ id, url, interval, screenshots }) => (
              <Table.Tr
                key={id}
                onClick={() => {
                  modal_data.current = {
                    type: "screenshots",
                    webpage: webpages.find((webpage) => webpage.id === id)!,
                  }
                  open_modal()
                }}
                className="cursor-pointer"
              >
                <Table.Td>
                  <a
                    onClick={(event) => event.stopPropagation()}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-blue-600 hover:underline"
                  >
                    {url}
                  </a>
                </Table.Td>
                <Table.Td pl={5}>
                  <div
                    onClick={(event) => event.stopPropagation()}
                    style={{ display: "inline-block" }}
                  >
                    <Select
                      value={interval}
                      data={["minute", "hour", "day"]}
                      allowDeselect={false}
                      onChange={async (value) => {
                        const new_interval = value as "minute" | "hour" | "day"

                        try {
                          const { error: err, data } = await fetch.POST(
                            "/api/webpage",
                            {
                              headers: {
                                "X-CSRFToken": csrf.current,
                              },
                              body: {
                                url,
                                interval: new_interval,
                              },
                            }
                          )

                          if (err) {
                            console.error(err) // TODO better error handling
                          } else {
                            setWebpages((prev) =>
                              prev.map((webpage) =>
                                webpage.url === url
                                  ? { ...webpage, interval: new_interval }
                                  : webpage
                              )
                            )
                            notifications.show({
                              message: `Webpage "${data.url}" is now being monitored every "${data.interval}", instead of every "${interval}".`,
                              withCloseButton: false,
                              autoClose: 3000,
                              color: "green",
                            })
                          }
                        } catch (err) {
                          console.error(err) // TODO better error handling
                        }
                      }}
                      style={{ maxWidth: "120px" }}
                      styles={{ input: { paddingLeft: "6px" } }}
                    />
                  </div>
                </Table.Td>
                <Table.Td ta="center">{screenshots.length}</Table.Td>
                <Table.Td ta="center">
                  <Button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation()
                      modal_data.current = {
                        type: "delete",
                        webpage: webpages.find((webpage) => webpage.id === id)!,
                      }
                      open_modal()
                    }}
                    color="red"
                  >
                    <MdDelete />
                  </Button>
                </Table.Td>
              </Table.Tr>
            ))}

            <Table.Tr className="no-hover">
              <Table.Td pl={5}>
                <form
                  id="form_create_webpage"
                  onSubmit={form.onSubmit(async (form_values) => {
                    if (
                      webpages.find(
                        (webpage) =>
                          webpage.url.replace(/\/$/, "") ===
                          form_values.url.replace(/\/$/, "")
                      )
                    ) {
                      form.setFieldError("url", "Already being monitored")
                      notifications.show({
                        message: `Webpage "${form_values.url}" is already being monitored.`,
                        withCloseButton: false,
                        autoClose: 3000,
                        color: "red",
                      })

                      return
                    }

                    try {
                      const { error: err, data } = await fetch.POST(
                        "/api/webpage",
                        {
                          headers: {
                            "X-CSRFToken": csrf.current,
                          },
                          body: form_values,
                        }
                      )

                      if (err) {
                        console.error(err)
                      } else {
                        setWebpages((prev) => [
                          ...prev,
                          {
                            interval: data.interval,
                            url: data.url,
                            id: data.id,
                            screenshots: [],
                          },
                        ])
                        notifications.show({
                          message: `Webpage "${data.url}" is now successfully being monitored every "${data.interval}".`,
                          withCloseButton: false,
                          autoClose: 3000,
                          color: "green",
                        })
                      }
                    } catch (err) {
                      console.error(err) // TODO better error handling
                    } finally {
                      form.reset()
                    }
                  })}
                >
                  <TextInput
                    key={form.key("url")}
                    placeholder="https://example.com/"
                    style={{ maxWidth: "360px" }}
                    styles={{ input: { paddingLeft: "6px" } }}
                    {...form.getInputProps("url")}
                  />
                </form>
              </Table.Td>
              <Table.Td pl={5}>
                <Select
                  form="form_create_webpage"
                  key={form.key("interval")}
                  data={["minute", "hour", "day"]}
                  allowDeselect={false}
                  style={{ maxWidth: "120px" }}
                  styles={{ input: { paddingLeft: "6px" } }}
                  {...form.getInputProps("interval")}
                />
              </Table.Td>
              <Table.Td ta="center">-</Table.Td>
              <Table.Td ta="center">
                <Button
                  type="submit"
                  form="form_create_webpage"
                  onClick={(event) => event.stopPropagation()}
                  color="green"
                >
                  <MdAdd />
                </Button>
              </Table.Td>
            </Table.Tr>
          </Table.Tbody>
        </Table>
      </main>
    </>
  )
}

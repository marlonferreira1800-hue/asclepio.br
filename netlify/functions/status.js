export default async (request, context) => {
  return new Response(
    JSON.stringify({
      status: "online",
      plataforma: "Netlify Serverless",
      banco: "memoria",
      timestamp: new Date().toISOString(),
    }),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
      },
    }
  );
};

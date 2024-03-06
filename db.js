const {MongoClient}=require('mongodb')
const uri="mongodb+srv://kyadavalli04:<password>@cluster0.2o0bzi6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


async function dbConnect(){
    const client = new MongoClient(uri);
    await client.connect();
    try{
        await client.connect();
    await listDatabases(client);
    }
    catch(e){
       console.error(e)
    }
    finally{
        await client.close();
    }
}


module.exports= dbConnect;